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

  // Send an email
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
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch('/emails/' + mailbox)
  .then(response => response.json())
  .then(emails => {
      // Print emails
      console.log(emails);
      // Run add_email function for each email in emails
      emails.forEach(add_email);
  });

  function add_email(contents) {
    
    // Create new post
    const post = document.createElement('div');
    post.className = 'post';
    post.addEventListener('click', function() {
      load_mail(contents.id)
    });
    post.innerHTML = `<li class="list-group-item">${contents.sender} || ${contents.subject} || ${contents.timestamp}</li>`;

    // Add post to DOM
    document.querySelector('#emails-view').append(post);
  };
}


function load_mail(id) {

  // Show the mailbox and hide other views
  document.querySelector('#email-view').style.display = 'block';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  fetch('/emails/' + id)
  .then(response => response.json())
  .then(email => {
      // Print email
      console.log(email);

      // Create new post
      const post = document.createElement('div');
      post.className = 'post';
      post.innerHTML = `<h3>${email.sender}</h3> <h3>${email.subject}</h3> <h3>${email.timestamp}</h3>`;

      // Show the email name
      document.querySelector('#email-view').innerHTML = `<h3>${email.subject.charAt(0).toUpperCase() + email.subject.slice(1)}</h3>`;
      // Add post to DOM
      document.querySelector('#email-view').append(post);
  });
}