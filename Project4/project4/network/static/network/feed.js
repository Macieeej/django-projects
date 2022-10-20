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
  console.log("Hello world!");
  
  var id = post.querySelector("#post_id").innerHTML;
  post.querySelector('#post_body').style.display = 'none';
  post.querySelector('#edit-form').style.display = 'block';
  //post.querySelector('#compose-body').value = "dsdcdcs";
  // Get the email using api
  fetch('/posts/' + id, {
    method: 'GET' })
  .then(response => response.json())
  .then(fetchedPost => {
    post.querySelector('#compose-body').value = fetchedPost.body;
  });


  /*post.querySelector('#edit-form').addEventListener('click', function() {
    fetch('/posts/' + id, {
      method: 'PUT',
      body: JSON.stringify({
          body: post.querySelector('#compose-body').value
      })
    })
    e.preventDefault()
  });;*/

      post.querySelector('#edit-form').onclick = (e) => {
    fetch('/posts/' + id, {
      method: 'PUT',
      body: JSON.stringify({
          body: post.querySelector('#compose-body').value
      })
    })
    //e.preventDefault()
  } 
}



function load_like(post) {

}