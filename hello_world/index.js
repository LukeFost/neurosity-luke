const express = require("express");
const { Neurosity } = require("@neurosity/sdk");
require("dotenv").config();

const deviceId = process.env.DEVICE_ID || "";
const email = process.env.EMAIL || "";
const password = process.env.PASSWORD || "";
const app = express();
const port = 3001;

const verifyEnvs = (email, password, deviceId) => {
  const invalidEnv = (env) => {
    return env === "" || env === 0;
  };
  if (invalidEnv(email) || invalidEnv(password) || invalidEnv(deviceId)) {
    console.error(
      "Please verify deviceId, email and password are in .env file, quitting..."
    );
    process.exit(0);
  }
};
verifyEnvs(email, password, deviceId);

console.log(`${email} attempting to authenticate to ${deviceId}`);

const neurosity = new Neurosity({
  deviceId,
  timesync: true,
});

const main = async () => {
  try {
    await neurosity
      .login({
        email,
        password,
      })
      .catch((error) => {
        console.log(error);
        throw new Error(error);
      });
    console.log("Logged in");
  } catch (error) {
    console.log("error", error);
  }
};

main();

app.use(express.json());

let brainwaveData = [];
app.post("/train", async (req, res) => {
  const action = req.query.action; // 'start' or 'stop'
  let subscription;

  if (action === "start") {
    res.json({ message: "Training started" });
    subscription = neurosity.brainwaves("raw").subscribe((brainwaves) => {
      brainwaveData.push(brainwaves);
      console.log(brainwaves);
    });
  } else if (action === "stop") {
    res.json({ message: "Training stopped" });
    subscription.unsubscribe();
    brainwaveData = []; // Clear the data after stopping
  } else {
    res.status(400).json({ message: "Invalid action" });
  }
});

// Endpoint to send EEG data
app.get("/get-eeg-data", (req, res) => {
  res.json(brainwaveData);
  brainwaveData = []; // Clear after sending
});
