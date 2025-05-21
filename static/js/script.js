// Basic form validation
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.querySelector('.upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('video');
            if (fileInput.files.length === 0) {
                e.preventDefault();
                alert('Please select a video file to upload');
                return false;
            }
            
            const file = fileInput.files[0];
            const maxSize = 50 * 1024 * 1024; // 50MB
            
            if (file.size > maxSize) {
                e.preventDefault();
                alert('File size exceeds 50MB limit');
                return false;
            }
            
            return true;
        });
    }
});