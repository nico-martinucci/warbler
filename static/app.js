"use strict";

// Add event listener to the element with id of messages
// Target by LI

const API_ENDPOINT_URL = "http://localhost:5001/api";
const $messagesList = $("#messages");
const mytoken = "{{ csrf_token() }}";

$messagesList.on("click", ".messages-like", handleStarClick)

async function handleStarClick(event) {
    event.preventDefault();

    const $star = $(event.target)
    const message_id = $star.closest("li").attr("id");

    const response = await axios({
        url: `${API_ENDPOINT_URL}/messages/${message_id}/likes`,
        method: "POST",
        data: {
            csrf_token: mytoken
        }
    })

    $star.toggleClass("bi-star").toggleClass("bi-star-fill")
}