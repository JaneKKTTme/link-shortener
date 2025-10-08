function copyToClipboard() {
    const shortLink = document.getElementById('short-link');
    const textArea = document.createElement('textarea');
    textArea.value = shortLink.textContent;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
            
    const message = document.getElementById('copy-message');
    message.style.display = 'block';
    setTimeout(() => {
        message.style.display = 'none';
    }, 2000);
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.container').style.opacity = '0';
    document.querySelector('.container').style.transform = 'translateY(20px)';
            
    setTimeout(() => {
        document.querySelector('.container').style.transition = 'all 0.6s ease';
        document.querySelector('.container').style.opacity = '1';
        document.querySelector('.container').style.transform = 'translateY(0)';
    }, 100);
});