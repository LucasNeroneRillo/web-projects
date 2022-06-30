document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email());

  // Create a div to displaying emails
  let div = document.createElement('div');
  div.setAttribute('id', 'email-view');
  document.querySelector('body').append(div);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email(email) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';

  // If email variable exists, show default reply view
  if (email) {
    document.querySelector('#compose-recipients').value = email.sender;
    if (email.subject.slice(0,3) === 'Re:') {
      document.querySelector('#compose-subject').value = `${email.subject}`;
    } else {
      document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
    }
    document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
  }
  // Else, clear out composition fields
  else {    
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
  }

  // Clear any previous error message
  const old_message = document.getElementById('error-message')
  if (old_message) {
    old_message.remove();
  }

  // Send email after submit event is triggered
  document.querySelector('form').onsubmit = () => {
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
      })
    })
    .then(response => response.json())
    .then(result => {
      if (!result.error) {
        // Email sent successfully! Redirect user to sent mailbox.
        load_mailbox('sent');
      } else {
        // If there was an error message already, delete it and then create new one
        const old_message = document.getElementById('error-message')
        if (old_message) {
          old_message.style.animation = 'disappear 0.3s';
          old_message.addEventListener('animationend', () => {
            old_message.remove();
            createErrorMessage(result.error)
          });
        // Else, only create an error message
        } else {
          createErrorMessage(result.error)
        }
      }
    });
    return false;
  };
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Get the emails from that mailbox
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    if (emails.error) {
      // Display error message to user
      document.querySelector('#email-view').innerHTML = `<div class="container">${email.error}</div>`;
    } else {
      // Add all emails from mailbox to view
      for (var key in emails) {

        // Create an HTML element for that email
        let email = emails[key];
        let element = document.createElement('div');
        element.setAttribute('class', 'container-fluid border border-dark py-2');

        // Gray background if email was read
        if (email.read) {
          element.style.backgroundColor = '#e0e0e0';
        }

        // Put basic info of the email inside the element
        element.innerHTML = 
          `<span><strong class="pr-3">${email.sender}</strong>${email.subject}</span>
          <span class='float-right text-secondary'>${email.timestamp}</span>`;

        // Make email be loaded when element is clicked
        element.style.cursor = 'pointer';
        element.addEventListener('click', () => {
          load_email(email.id);
        });

        // Create container for element
        let container = document.createElement('div');
        container.setAttribute('class', 'container-fluid px-0');
        container.style.position = 'relative';
        container.append(element);

        // Add button to archive/unarchive if mailbox is not "Sent"
        if (mailbox !== 'sent') {
          let btn = document.createElement('button');
          btn.setAttribute('class', 'btn btn-secondary float-right');
          btn.style.position = 'absolute';
          btn.style.right = '0';
          btn.hidden = true;
          if (mailbox === 'inbox') {
            btn.innerHTML = 'Archive';
          } else {
            btn.innerHTML = 'Unarchive';
          }

          // Add button to element's container
          container.prepend(btn);
          container.addEventListener('mouseover', () => {btn.hidden = false});
          container.addEventListener('mouseout', () => {btn.hidden = true});

          // Trigger button's action
          btn.onclick = () => {

            // Archive if email is unarchived, otherwise unarchive it
            let archive = true;
            if (mailbox === 'archive') {
              archive = false;
            }

            // Send info to server
            fetch(`/emails/${email.id}`, {
              method: 'PUT',
              body: JSON.stringify({
                  archived: archive
              })
            })
            .then( () => {
              // Redirect user to inbox page
              load_mailbox('inbox');
            });
          };
        }
        
        // Add container to view
        document.querySelector('#emails-view').append(container);
      }
    }
  });
}

function load_email(email_id) {
  
  // Show the email view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  // Clear out the div
  document.querySelector('#email-view').innerHTML = '';

  // Get the email by its id
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    if (email.error) {
      // Display error message to user
      document.querySelector('#email-view').innerHTML = `<div class="container">${email.error}</div>`;
    } else {
      // Update page's HTML
      document.querySelector('#email-view').innerHTML = `
        <div class="container">
          <p class="my-0"><strong>From: </strong>${email.sender}</p>
          <p class="my-0"><strong>To: </strong>${email.recipients}</p>
          <p class="my-0"><strong>Subject: </strong>${email.subject}</p>
          <p class="my-0"><strong>Timestamp: </strong>${email.timestamp}</p>
          <button class="btn btn-sm btn-outline-primary" id="reply">Reply</button>
          <hr>
          <p>${email.body}</p>
        </div>`;

      // Mark email as read
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({read: true})
      });

      // Make reply button work
      document.querySelector('#reply').addEventListener('click', () => {
        compose_email(email);
      })
    }
  });
}

function createErrorMessage(message) {
  let element = document.createElement('div');
  element.setAttribute('id', 'error-message');
  element.setAttribute('class', 'alert alert-danger');
  element.setAttribute('role', 'alert');
  element.innerHTML = message;
  document.querySelector('#compose-view').prepend(element);
}
