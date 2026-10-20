// Shopora Interactive JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                setTimeout(() => alert.remove(), 300);
            });
        }
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                setTimeout(() => alert.remove(), 500);
            }
        }, 5000);
    });

    // 2. Quantity Stepper (+ / -)
    const qtyWrappers = document.querySelectorAll('.quantity-control');
    qtyWrappers.forEach(wrap => {
        const input = wrap.querySelector('.quantity-input');
        const minusBtn = wrap.querySelector('.btn-qty-minus');
        const plusBtn = wrap.querySelector('.btn-qty-plus');

        if (input && minusBtn && plusBtn) {
            const min = parseInt(input.getAttribute('min') || '1', 10);
            const max = parseInt(input.getAttribute('max') || '999', 10);

            minusBtn.addEventListener('click', () => {
                let val = parseInt(input.value, 10) || min;
                if (val > min) {
                    input.value = val - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });

            plusBtn.addEventListener('click', () => {
                let val = parseInt(input.value, 10) || min;
                if (val < max) {
                    input.value = val + 1;
                    input.dispatchEvent(new Event('change'));
                }
            });

            input.addEventListener('change', () => {
                let val = parseInt(input.value, 10);
                if (isNaN(val) || val < min) input.value = min;
                if (val > max) input.value = max;
            });
        }
    });

    // 3. Product Detail Gallery Thumbnail Switcher
    const mainImg = document.getElementById('main-gallery-image');
    const thumbs = document.querySelectorAll('.thumb-box');
    thumbs.forEach(thumb => {
        thumb.addEventListener('click', () => {
            const newSrc = thumb.getAttribute('data-large');
            if (mainImg && newSrc) {
                mainImg.src = newSrc;
                thumbs.forEach(t => t.classList.remove('active'));
                thumb.classList.add('active');
            }
        });
    });

    // 4. Interactive Indian PIN Code Checker
    const pincodeBtn = document.getElementById('btn-check-pincode');
    const pincodeInput = document.getElementById('pincode-input');
    const pincodeResult = document.getElementById('pincode-result');

    if (pincodeBtn && pincodeInput && pincodeResult) {
        const doCheck = () => {
            const val = pincodeInput.value.trim();
            if (!val || val.length !== 6 || !/^\d{6}$/.test(val)) {
                pincodeResult.innerHTML = '<span style="color: #ef4444;">Please enter a valid 6-digit Indian PIN code.</span>';
                return;
            }

            pincodeResult.innerHTML = '<span style="color: #64748b;">Checking serviceability for ' + val + '...</span>';

            fetch(`/api/check-pincode/?pincode=${encodeURIComponent(val)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.valid) {
                        pincodeResult.innerHTML = `
                            <div style="color: #15803d; font-size: 0.85rem; margin-top: 0.35rem;">
                                &#10003; <strong>${data.delivery_estimate}</strong> | <span style="color: #0284c7;">FREE Delivery</span><br>
                                <span style="color: #475569;">Cash on Delivery is available for PIN ${data.pincode}.</span>
                            </div>
                        `;
                    } else {
                        pincodeResult.innerHTML = `<span style="color: #ef4444;">${data.message}</span>`;
                    }
                })
                .catch(() => {
                    pincodeResult.innerHTML = '<span style="color: #15803d;">&#10003; Standard Delivery in 2-3 Days. Free Delivery eligible.</span>';
                });
        };

        pincodeBtn.addEventListener('click', doCheck);
        pincodeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                doCheck();
            }
        });
    }

    // 5. Wishlist AJAX Toggle
    const wishlistBtns = document.querySelectorAll('.wishlist-toggle-btn');
    wishlistBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const productId = btn.getAttribute('data-product-id');
            if (!productId) return;

            fetch(`/wishlist/toggle/${productId}/`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => {
                if (res.redirected) {
                    window.location.href = res.url;
                    return;
                }
                return res.json();
            })
            .then(data => {
                if (data && data.success) {
                    if (data.added) {
                        btn.classList.add('active');
                        btn.innerHTML = '&#9829;'; // Filled heart
                    } else {
                        btn.classList.remove('active');
                        btn.innerHTML = '&#9825;'; // Empty heart
                    }
                    // Update header wishlist counter
                    const headerBadge = document.getElementById('header-wishlist-counter');
                    if (headerBadge) {
                        headerBadge.textContent = data.wishlist_count;
                    }
                }
            })
            .catch(() => {
                // Fallback to normal navigation
                window.location.href = `/wishlist/toggle/${productId}/`;
            });
        });
    });

    // 6. Remove item confirmation
    const removeForms = document.querySelectorAll('.remove-item-form');
    removeForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!confirm('Are you sure you want to remove this item from your cart?')) {
                e.preventDefault();
            }
        });
    });
});
