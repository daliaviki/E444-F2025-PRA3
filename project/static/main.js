(function () { console.log("ready!"); })();

const postElements = document.getElementsByClassName("entry");
for (let i = 0; i < postElements.length; i++) {
  postElements[i].addEventListener("click", function () {
    const postId = this.getElementsByTagName("h2")[0].getAttribute("id");
    const node = this;
    fetch(`/delete/${postId}`)
      .then((resp) => resp.json())
      .then((result) => {
        if (result.status === 1) node.parentNode.removeChild(node);
        location.reload();
      })
      .catch((err) => console.log(err));
  });
}
