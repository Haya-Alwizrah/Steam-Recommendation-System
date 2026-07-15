document.addEventListener('DOMContentLoaded', () => {
    const backBtn = document.getElementById('global-back-btn');
    if (backBtn) {
        backBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = '/'; 
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

    const chartSelector = document.getElementById('chartSelector');
    if (chartSelector) {
        chartSelector.addEventListener('change', (e) => {
            const selectedId = e.target.value;
            const boxes = document.querySelectorAll('.chart-box');
            
            boxes.forEach(box => {
                if (box.id === selectedId) {
                    box.classList.add('active');
                } else {
                    box.classList.remove('active');
                }
            });
        });
    }
});