document.addEventListener("DOMContentLoaded", function () {
  const checkbox = document.getElementById("togglePassword");
  const passwordField = document.getElementById("passwordField");

  checkbox.addEventListener("change", () => {
    passwordField.type = checkbox.checked ? "text" : "password";
  });
});
