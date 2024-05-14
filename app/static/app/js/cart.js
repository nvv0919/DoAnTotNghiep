var updateBtns = document.getElementsByClassName('update-cart');
for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener("click", function () {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        console.log('productId: ' + productId, ' action: ' + action)
        console.log('user', user)
        if (user === "AnonymousUser") {
            console.log('Chưa đăng nhập')
        } else {
            updateUserOrder(productId, action)
        }
    })
}

function getCookie(name) {
    const cookieValue = document.cookie
        .split(';')
        .map(cookie => cookie.trim())
        .find(cookie => cookie.startsWith(name + '='));

    if (cookieValue) {
        return cookieValue.split('=')[1];
    }

    return null;
}

function updateUserOrder(productId, action) {
    const url = '/update_item/';
    const csrftoken = getCookie('csrftoken');

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action })
    })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            console.log('data', data);
            location.reload();
        });
}