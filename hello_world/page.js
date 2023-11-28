const express = require("express");
const axios = require("axios");
const app = express();
const port = 3000;

app.use(express.static("public"));

app.get("/control-training", async (req, res) => {
  const action = req.query.action; // 'start' or 'stop'

  try {
    const response = await axios.post(
      `http://localhost:3001/train?action=${action}`
    );
    res.send(response.data.message);
  } catch (error) {
    console.error(`Error: ${error}`);
    res.status(500).send("Server error");
  }
});

app.listen(port, () => {
  console.log(`Web server running at http://localhost:${port}`);
});
