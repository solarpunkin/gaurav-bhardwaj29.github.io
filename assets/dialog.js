
document.addEventListener('DOMContentLoaded', () => {
  const dialogBox = document.getElementById('dialogBox');
  const closeButton = document.getElementById('closeButton');
  const cancelButton = document.getElementById('cancelButton');
  const okButton = document.getElementById('okButton');
  const dialogMessage = document.getElementById('dialogMessage');
  const overlay = document.getElementById('overlay');

  const messages = [
    `If you're reading this... 
    Congratulations, you're alive. 
    If that's not something to smile about, 
    then I don't know what is`,

    `Odds are you haven't seen light today. 
    Take a walk—you could use some color`,

    `Look up. The sky's bigger than the city walls. 
    Catch it while you can`,

    `Still gooning at this glowing rectangle?`,

    `Maybe music will save you: 
    <i>Open your eyes, Look up to the skies and see...</i>`,

    `I am officially out of help messages. 
    <i>Sorry for being a jerk</i>`
  ];

  let messageIndex = 0;

  function showDialog() {
    const audio = new Audio('assets/error.wav');
    audio.play();
    dialogMessage.innerHTML = messages[messageIndex];
    dialogBox.style.display = 'block';
    overlay.style.display = 'block';
  }

  function hideDialog() {
    dialogBox.style.display = 'none';
    overlay.style.display = 'none';
  }

  function nextMessage() {
    messageIndex++;
    if (messageIndex < 5) {
      dialogMessage.innerHTML = messages[messageIndex];
    } else {
      dialogMessage.innerHTML = messages[5];
      cancelButton.style.display = 'none';
      okButton.style.margin = '0 auto';
      okButton.style.float = 'none';
    }
  }

  closeButton.addEventListener('click', hideDialog);
  okButton.addEventListener('click', hideDialog);
  cancelButton.addEventListener('click', nextMessage);

  showDialog();
});
