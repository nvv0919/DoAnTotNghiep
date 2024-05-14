document.addEventListener("DOMContentLoaded", function () {
    var paymentMethodDirect = document.getElementById("payment-method-direct");
    var paymentMethodOnline = document.getElementById("payment-method-online");

    // Thêm sự kiện click cho nút "Thanh toán"
    document.querySelector(".btn.btn-primary").addEventListener("click", function () {
        if (paymentMethodDirect.checked) {
            // Chuyển hướng đến trang chủ
            window.location.href = "{% url 'home' %}";
        } else if (paymentMethodOnline.checked) {
            // Chuyển hướng đến trang thanh toán trực tuyến
            window.location.href = "{% url 'payment' %}";
        }
    });
});
