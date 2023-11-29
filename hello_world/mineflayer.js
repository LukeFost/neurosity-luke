const mineflayer = require("mineflayer");
const axios = require("axios"); // Make sure to npm install axios
const { mineflayer: mineflayerViewer } = require("prismarine-viewer");
const {
  pathfinder,
  Movements,
  goals: { GoalFollow },
} = require("mineflayer-pathfinder");

let lastPosition = null;
let lastYaw = null;

const bot = mineflayer.createBot({
  host: "localhost", // minecraft server ip
  username: "User", // username or email, switch if you want to change accounts
  port: 25565, // only set if you need a port that isn't 25565
  // password: '12345678'        // set if you want to use password-based auth (may be unreliable). If specified, the `username` must be an email
});

bot.loadPlugin(pathfinder);
let followedPlayer = null;
function followPlayer() {
  const checkForPlayer = setInterval(() => {
    const player = bot.players["Malgaph"]; // Replace with the correct username

    if (player && player.entity) {
      console.log("Player found. Starting to follow.");
      clearInterval(checkForPlayer);

      followedPlayer = player.entity;

      const mcData = require("minecraft-data")(bot.version);
      const movements = new Movements(bot, mcData);
      bot.pathfinder.setMovements(movements);

      bot.pathfinder.setGoal(new GoalFollow(player.entity, 3), true);
    } else {
      console.log("Player not in range, checking again...");
    }
  }, 1000); // check every second
}

bot.on("spawn", followPlayer);

function updateClassification(classification) {
  axios
    .post("http:///127.0.0.1:3002/update-classification", { classification })
    .then((response) =>
      console.log(`Classification updated: ${response.data.message}`)
    )
    .catch((error) => console.error("Error updating classification:", error));
}

function getTurnDirection(lastYaw, currentYaw) {
  const deltaYaw = ((currentYaw - lastYaw + Math.PI) % (2 * Math.PI)) - Math.PI;

  if (deltaYaw > 0) return "_left";
  if (deltaYaw < 0) return "_right";
  return ""; // No significant turn
}

setInterval(() => {
  if (!followedPlayer) return;

  const currentPos = followedPlayer.position;
  const currentYaw = followedPlayer.yaw;
  let classification = "not_moving";

  // Determine if the player has moved
  if (lastPosition && currentPos.distanceTo(lastPosition) > 0.1) {
    classification = "walking";
  }

  // Determine if the player has turned
  if (lastYaw !== null) {
    const turnDirection = getTurnDirection(lastYaw, currentYaw);
    if (Math.abs(currentYaw - lastYaw) > Math.PI / 8) {
      classification += turnDirection;
    }
  }

  // Update classification
  updateClassification(classification);

  lastPosition = currentPos.clone();
  lastYaw = currentYaw;
}, 500); // Check every second, adjust as needed
