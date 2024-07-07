function validatePhoneNumber() {
    const country = document.getElementById('country').value;
    const phone = document.getElementById('phone').value;
    let valid = false;
    let message = '';

    switch (country) {
        case '+1':
            valid = /^\d{10}$/.test(phone);
            message = 'Le numéro de téléphone doit contenir 10 chiffres pour les États-Unis/Canada.';
            break;
        case '+33':
            valid = /^\d{9}$/.test(phone);
            message = 'Le numéro de téléphone doit contenir 9 chiffres pour la France.';
            break;
        case '+44':
            valid = /^\d{10}$/.test(phone);
            message = 'Le numéro de téléphone doit contenir 10 chiffres pour le Royaume-Uni.';
            break;
        case '+49':
            valid = /^\d{10}$/.test(phone);
            message = 'Le numéro de téléphone doit contenir 10 chiffres pour l’Allemagne.';
            break;
        default:
            valid = true;
            break;
    }

    if (!valid) {
        alert(message);
    }

    return valid;
}
