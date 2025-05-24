document.addEventListener('DOMContentLoaded', () => {
    // Animar botones al hacer clic
    const buttons = document.querySelectorAll('.btn-secondary-custom, .btn-outline-secondary, .btn-outline-primary, .btn-outline-success');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 100);
        });
    });

    // Animar mensajes del chat
    const messages = document.querySelectorAll('.chat-message');
    messages.forEach((message, index) => {
        message.style.animationDelay = `${index * 0.3}s`;
    });

    // Animar elementos de la lista
    const listItems = document.querySelectorAll('.list-group-item');
    listItems.forEach((item, index) => {
        item.style.animation = 'fadeIn 0.5s ease-in-out';
        item.style.animationDelay = `${index * 0.2}s`;
    });
});