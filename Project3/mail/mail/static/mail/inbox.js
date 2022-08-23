document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // Send an email and load sent mailbox
  document.querySelector('form').onsubmit = function() {
    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: document.querySelector('#compose-recipients').value,
            subject: document.querySelector('#compose-subject').value,
            body: document.querySelector('#compose-body').value
        })
    })
    .then(response => load_mailbox('sent'));
    return false;
  };
}


function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3><div id='rh1'>From:</div><div id='rh2'>Title:</div><div id='rh3'>Date:</div>`;

  // Get the mailbox using api
  fetch('/emails/' + mailbox)
  .then(response => response.json())
  .then(emails => {
 
      // Run add_email function for each email in emails
      emails.forEach(add_email);
  });

  function add_email(email) {
    
    // Create new post
    const element = document.createElement('div');
    // Add on click functionality
    element.addEventListener('click', function() {

      load_mail(email.id)
    });

    // Check if item is marked as read and change its html class
    if (email.read) {
      element.className = 'read';
    } else {
      element.className = 'unread';
    }

    element.innerHTML = `<div id='r1'>${email.sender}</div> <div id='r2'>${email.subject}</div> <div id='r3'>${email.timestamp}</div>`;

    // Add post to DOM
    document.querySelector('#emails-view').append(element);
  };
}


function load_mail(id) {

  // Show the mailbox and hide other views
  document.querySelector('#email-view').style.display = 'block';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Mark clicked email as read
  fetch('/emails/'+id, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  });

  // Get the email using api
  fetch('/emails/' + id)
  .then(response => response.json())
  .then(email => {

      // Create new post
      const element = document.createElement('div');
      element.className = 'displayEmail';
      element.innerHTML = `
      <h6>From: ${email.sender}</h6>
      <h6>To: ${email.recipients}</h6>
      <h6>${email.timestamp}</h6><hr>
      <h5>${email.subject}</h5>
      <a>${email.body}</a>`;

      // Show the email
      document.querySelector('#email-view').innerHTML = element.innerHTML;
  });
}