// JavaScript functions
function showApplyBar() {
    var bar = document.getElementById('apply-success-bar');
    if (bar) {
        bar.style.display = 'block';
        setTimeout(function() {
            bar.style.display = 'none';
        }, 2000);
    }
}
