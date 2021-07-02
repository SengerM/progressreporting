window.onscroll = function() {myFunction()};

var header = document.getElementById("presentation_header");
var sticky = header.offsetTop;

var sticked_header = header.cloneNode(true);
sticked_header.id = "sticked_presentation_header";
document.body.appendChild(sticked_header);

function myFunction() {
	if (window.pageYOffset > sticky) {
		sticked_header.classList.add("show_header");
	} else {
		sticked_header.classList.remove("show_header");
	}
}
