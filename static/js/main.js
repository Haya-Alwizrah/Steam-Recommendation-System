document.addEventListener('DOMContentLoaded', () => {
    const backBtn = document.getElementById('global-back-btn');
    if (backBtn) {
        backBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (window.history.length > 1 && document.referrer !== "") {
                window.history.back();
            } else {
                window.location.href = '/';
            }
        });
    }

    const tabBtns = document.querySelectorAll('.tab-btn');
    const chartViews = document.querySelectorAll('.chart-view');

    if (tabBtns.length > 0) {
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                chartViews.forEach(v => v.classList.remove('active'));

                btn.classList.add('active');

                const targetId = btn.getAttribute('data-target');
                const targetView = document.getElementById(targetId);
                if (targetView) {
                    targetView.classList.add('active');
                }
            });
        });
    }
});