const button = document.querySelector("#newPost");

button.addEventListener("click", newPost);

function newPost(e) {
    e.preventDefault();
    window.location = "/newpost"
}
