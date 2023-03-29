document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  let posts = document.querySelectorAll('div.single_post');
  posts.forEach(post => {
    post.querySelector('#edit-form').style.display = 'none';
    post.querySelector('#edit').addEventListener('click', () => load_edit(post));
    post.querySelector('#like').addEventListener('click', () => load_like(post));
  });

});

function load_edit(post) {
  
  // Get post's ID
  var id = post.querySelector("#post_id").value;

  // Hide post body, display textarea instead
  post.querySelector('#post_body').style.display = 'none';
  post.querySelector('#edit-form').style.display = 'block';

  // Get the post using api, preprend textareap with body content
  fetch('/posts/' + id, {
    method: 'GET' })
  .then(response => response.json())
  .then(fetchedPost => {
    post.querySelector('#compose-body').value = fetchedPost.body;
  });

  // Send edited post using api
  post.querySelector('#save-button').onclick = () => {
    fetch('/posts/' + id, {
      method: 'PUT',
      body: JSON.stringify({
          body: post.querySelector('#compose-body').value
      })
    })
    .then(() => {
      post.querySelector('#edit-form').style.display = 'none'
      post.querySelector('#post_body').style.display = 'block';
      post.querySelector('#post_body').innerHTML = post.querySelector('#compose-body').value;
    });
  } 
}



function load_like(post) {
  
  // Get post's ID
  var id = post.querySelector("#post_id").value;

  // Send edited post using api
  fetch('/posts/' + id, {
    method: 'PUT',
    body: JSON.stringify({
        likes: 2
    })
  })
  .then(() => {
    post.querySelector('#post_likes').innerHTML = post.querySelector('#post_likes').innerHTML;
  });
  

}