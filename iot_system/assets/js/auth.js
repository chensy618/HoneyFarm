function validateLogin(user, pass) {
  if (!user || !pass) return false;

  if (user === "admin" && pass === "admin123") {
    return true;
  }

  if (user === "root" && pass === "toor") {
    return true;
  }

}
