
document.addEventListener('DOMContentLoaded', () => {
  const dialogBox = document.getElementById('dialogBox');
  const closeButton = document.getElementById('closeButton');
  const cancelButton = document.getElementById('cancelButton');
  const okButton = document.getElementById('okButton');
  const dialogMessage = document.getElementById('dialogMessage');
  const overlay = document.getElementById('overlay');

  const messages = [
    "Is this the real life?",
    "Is this just fantasy?",
    "Caught in a landslide,",
    "No escape from reality.",
    "Open your eyes,",
    "Look up to the skies and see."
  ];

  let messageIndex = 0;

  function showDialog() {
    dialogMessage.textContent = messages[messageIndex];
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
      dialogMessage.textContent = messages[messageIndex];
    } else {
      dialogMessage.textContent = messages[5];
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
