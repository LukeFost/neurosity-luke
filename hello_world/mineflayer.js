const mineflayer = require("mineflayer");
const axios = require("axios"); // Make sure to npm install axios
const { mineflayer: mineflayerViewer } = require("prismarine-viewer");
const {
  pathfinder,
  Movements,
  goals: { GoalFollow },
} = require("mineflayer-pathfinder");

let lastPosition = null;
let lastPitch = null;
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

function getPitchDirection(lastPitch, currentPitch) {
  if (currentPitch > lastPitch) return "_lookDown";
  if (currentPitch < lastPitch) return "_lookUp";
  return "";
}

function getMovementDirection(lastPosition, currentPosition, currentYaw) {
  if (!lastPosition) return "";

  // Calculate the difference in position
  const dx = currentPosition.x - lastPosition.x;
  const dz = currentPosition.z - lastPosition.z;

  // Calculate the angle of movement from the difference in position
  let moveAngle = Math.atan2(-dz, dx);

  // Adjust the moveAngle based on the player's current yaw
  moveAngle = (moveAngle - currentYaw + Math.PI * 2) % (Math.PI * 2);

  // Determine the direction of movement
  if (moveAngle < Math.PI / 4 || moveAngle > (7 * Math.PI) / 4) return "_right";
  if (moveAngle >= Math.PI / 4 && moveAngle < (3 * Math.PI) / 4)
    return "_forward";
  if (moveAngle >= (3 * Math.PI) / 4 && moveAngle < (5 * Math.PI) / 4)
    return "_left";
  if (moveAngle >= (5 * Math.PI) / 4 && moveAngle < (7 * Math.PI) / 4)
    return "_backward";

  return "";
}

setInterval(() => {
  if (!followedPlayer) return;

  const currentPosition = followedPlayer.position;
  const currentYaw = followedPlayer.yaw;
  let classification = "not_moving";

  if (lastPosition && currentPosition.distanceTo(lastPosition) > 0.1) {
    classification = "walking";
    classification += getMovementDirection(
      lastPosition,
      currentPosition,
      currentYaw
    );

    if (followedPlayer.isJumping) {
      classification += "_jumping";
    }
  }

  updateClassification(classification);

  lastPosition = currentPosition.clone();
  lastYaw = currentYaw;
}, 500);
