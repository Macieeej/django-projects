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

  // Send an email and load sent mailbox after pressing button
  document.querySelector('form').onsubmit = () => {
    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: document.querySelector('#compose-recipients').value,
            subject: document.querySelector('#compose-subject').value,
            body: document.querySelector('#compose-body').value
        })
    })
    .then(() => load_mailbox('sent'));
    return false;
  };
}


function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}`;
  document.querySelector('#emails-view').innerHTML += `</h3><div id='rh1'>From:</div><div id='rh2'>Title:</div><div id='rh3'>Date:</div>`;

  // Get the mailbox using api
  fetch('/emails/' + mailbox)
  .then(response => response.json())
  .then(emails => {
    emails.forEach(email => {
      const element = document.createElement('div');
      element.className = email.read ? 'read' : 'unread';
      element.innerHTML = `<div id='r1'>${email.sender}</div>
                          <div id='r2'>${email.subject}</div>
                          <div id='r3'>${email.timestamp}</div>`;
      element.addEventListener('click', () => { load_email(email.id) });
      document.querySelector('#emails-view').append(element);
    });
  });
}


function load_email(id) {

  // Show the mailbox and hide other views
  document.querySelector('#email-view').style.display = 'block';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Mark clicked email as read
  fetch('/emails/' + id, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  });

  // Get the email using api
  fetch('/emails/' + id)
  .then(response => response.json())
  .then(email => {
      // Create div for the email and display it
      const element = document.createElement('div');
      element.className = 'displayEmail';
      element.innerHTML = `<h6>From: ${email.sender}</h6>
                          <h6>To: ${email.recipients}</h6>
                          <h6>${email.timestamp}</h6><hr>
                          <h5>${email.subject}</h5>
                          <a>${email.body}</a><br><br>`;
      document.querySelector('#email-view').innerHTML = element.innerHTML;

      // Add archive/unarchive button
      const archiveButton = document.createElement('button');
      archiveButton.className = 'btn btn-sm btn-outline-primary';
      archiveButton.innerHTML = (email.archived) ? 'Unarchive' : 'Archive';
      archiveButton.addEventListener('click', () => {
        const archOrNot = (email.archived) ? false : true;
        fetch('/emails/' + id, {
          method: 'PUT',
          body: JSON.stringify({
              archived: archOrNot
          })
        })
        .then(() => load_mailbox('inbox'));
      });
      document.querySelector('#email-view').append(archiveButton);

      // Add reply button
      const replyButton = document.createElement('button');
      replyButton.className = 'btn btn-sm btn-outline-primary';
      replyButton.innerHTML = 'Reply';
      replyButton.addEventListener('click', function() {
        compose_email();
        document.querySelector('#compose-recipients').value = email.sender;
        if (email.subject.substring(0,3)=='Re:') {
          document.querySelector('#compose-subject').value = email.subject;
        }
        else {
          document.querySelector('#compose-subject').value = 'Re: ' + email.subject;
        }
        
        document.querySelector('#compose-body').value = '\n\nOn ' + email.timestamp + ' ' + email.sender + ' wrote:\n' + email.body;
      });
      document.querySelector('#email-view').append(replyButton);
  });
}