// Function to decrement the remaining time by one second
function decrementRemainingTime() {
  var remainingTimeElement = document.getElementById("remaining-time");
  var remainingTimeString = remainingTimeElement.innerText;
  var timeComponents = remainingTimeString.split(":");
  
  // Extract hours, minutes, and seconds
  var hours = parseInt(timeComponents[0]);
  var minutes = parseInt(timeComponents[1]);
  var seconds = parseInt(timeComponents[2]);
  
  // Check if remaining time is less than 30 seconds
  var lessThanThirtySeconds = hours === 0 && minutes === 0 && seconds <= 30;
  
  // Decrement the remaining time by one second
  if (seconds > 0) {
    seconds -= 1;
  } else {
    if (minutes > 0) {
      minutes -= 1;
      seconds = 59;
    } else {
      if (hours > 0) {
        hours -= 1;
        minutes = 59;
        seconds = 59;
      }
    }
  }
  
  // Format the new remaining time
  var newRemainingTimeString = formatTime(hours, minutes, seconds);
  
  // Update the remaining time displayed on the page
  remainingTimeElement.innerText = newRemainingTimeString;
  
  // Add blink and red classes if less than 30 seconds remaining
  if (lessThanThirtySeconds) {
    remainingTimeElement.classList.add("blink-red");
  }
  
  // Call this function recursively after one second
  setTimeout(decrementRemainingTime, 1000);
}

// Function to format time components (add leading zeros if necessary)
function formatTime(hours, minutes, seconds) {
  var formattedHours = hours.toString().padStart(2, '0');
  var formattedMinutes = minutes.toString().padStart(2, '0');
  var formattedSeconds = seconds.toString().padStart(2, '0');
  return formattedHours + ":" + formattedMinutes + ":" + formattedSeconds;
}

// Call the decrementRemainingTime function when the page loads
window.onload = function() {
  decrementRemainingTime();
};