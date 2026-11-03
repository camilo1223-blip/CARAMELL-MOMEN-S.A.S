// Gestión Global de Carrito y Estado de Usuario para CARAMELL MOMEN S.A.S.

const CartManager = {
    getCart() {
        const cart = localStorage.getItem('caramell_cart');
        return cart ? JSON.parse(cart) : [];
    },

    saveCart(cart) {
        localStorage.setItem('caramell_cart', JSON.stringify(cart));
        this.updateCounter();
    },

    addItem(producto, cantidad = 1) {
        let cart = this.getCart();
        const existingIndex = cart.findIndex(item => item.id_producto === producto.id_producto);

        if (existingIndex > -1) {
            const nuevaCantidad = cart[existingIndex].cantidad + cantidad;
            if (nuevaCantidad > producto.stock) {
                showToast(`Existencias insuficientes. Stock máximo: ${producto.stock}`, 'error');
                return false;
            }
            cart[existingIndex].cantidad = nuevaCantidad;
        } else {
            if (cantidad > producto.stock) {
                showToast(`Existencias insuficientes. Stock máximo: ${producto.stock}`, 'error');
                return false;
            }
            cart.push({
                id_producto: producto.id_producto,
                nombre: producto.nombre,
                precio: producto.precio,
                imagen_url: producto.imagen_url,
                stock: producto.stock,
                cantidad: cantidad
            });
        }

        this.saveCart(cart);
        showToast(`¡"${producto.nombre}" agregado al carrito!`, 'success');
        return true;
    },

    updateQuantity(id_producto, cantidad) {
        let cart = this.getCart();
        const item = cart.find(i => i.id_producto === id_producto);
        if (item) {
            if (cantidad <= 0) {
                this.removeItem(id_producto);
                return;
            }
            if (cantidad > item.stock) {
                showToast(`No puedes superar las existencias (${item.stock})`, 'error');
                return;
            }
            item.cantidad = cantidad;
            this.saveCart(cart);
        }
    },

    removeItem(id_producto) {
        let cart = this.getCart().filter(item => item.id_producto !== id_producto);
        this.saveCart(cart);
        showToast('Producto eliminado del carrito', 'info');
    },

    clearCart() {
        localStorage.removeItem('caramell_cart');
        this.updateCounter();
    },

    updateCounter() {
        const counter = document.getElementById('cart-counter');
        if (counter) {
            const totalItems = this.getCart().reduce((sum, item) => sum + item.cantidad, 0);
            counter.textContent = totalItems;
            counter.classList.toggle('animate-bounce', totalItems > 0);
            setTimeout(() => counter.classList.remove('animate-bounce'), 1000);
        }
    },

    getTotal() {
        return this.getCart().reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
    }
};

// Notificaciones Toast Modernas
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const bgColors = {
        success: 'bg-emerald-600 text-white',
        error: 'bg-rose-600 text-white',
        info: 'bg-[#3D2314] text-white',
        warning: 'bg-amber-500 text-white'
    };

    const icons = {
        success: '🍬',
        error: '⚠️',
        info: '✨',
        warning: '🔔'
    };

    toast.className = `flex items-center gap-3 px-4 py-3 rounded-2xl shadow-xl text-xs font-semibold transform transition-all duration-300 translate-y-2 opacity-0 pointer-events-auto ${bgColors[type] || bgColors.info}`;
    toast.innerHTML = `<span>${icons[type] || '🍬'}</span> <span>${message}</span>`;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    });

    setTimeout(() => {
        toast.classList.add('opacity-0', 'scale-90');
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Verificación de Autenticación de Usuario
async function checkAuthStatus() {
    try {
        const res = await fetch('/api/auth/me');
        const data = await res.json();

        const btnLogin = document.getElementById('btn-login-header');
        const loggedBox = document.getElementById('user-logged-box');
        const displayName = document.getElementById('user-display-name');
        const avatarInitial = document.getElementById('user-avatar-initial');
        const dropdownEmail = document.getElementById('dropdown-user-email');
        const adminLink = document.getElementById('nav-admin-link');
        const mobileAdminLink = document.getElementById('mobile-admin-link');
        const mobileLogin = document.getElementById('mobile-login-link');
        const mobileUnauth = document.getElementById('mobile-unauth-links');

        if (data.authenticated) {
            const user = data.usuario;
            if (btnLogin) btnLogin.classList.add('hidden');
            if (loggedBox) loggedBox.classList.remove('hidden');
            if (mobileUnauth) mobileUnauth.classList.add('hidden');
            if (mobileLogin) mobileLogin.classList.remove('hidden');
            if (displayName) displayName.textContent = user.nombre.split(' ')[0];
            if (avatarInitial) avatarInitial.textContent = user.nombre.charAt(0).toUpperCase();
            if (dropdownEmail) dropdownEmail.textContent = user.correo;

            if (user.rol === 'administrador') {
                if (adminLink) adminLink.classList.remove('hidden');
                if (mobileAdminLink) mobileAdminLink.classList.remove('hidden');
            }

            if (mobileLogin) {
                mobileLogin.textContent = 'Cerrar Sesión (' + user.nombre.split(' ')[0] + ')';
                mobileLogin.onclick = (e) => { e.preventDefault(); cerrarSesion(); };
            }
        } else {
            if (btnLogin) btnLogin.classList.remove('hidden');
            if (loggedBox) loggedBox.classList.add('hidden');
            if (adminLink) adminLink.classList.add('hidden');
            if (mobileAdminLink) mobileAdminLink.classList.add('hidden');
            if (mobileUnauth) mobileUnauth.classList.remove('hidden');
            if (mobileLogin) mobileLogin.classList.add('hidden');
        }
    } catch (err) {
        console.error('Error al validar sesión:', err);
    }
}

// Cerrar sesión
async function cerrarSesion() {
    try {
        const res = await fetch('/api/auth/logout', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showToast('Has cerrado sesión correctamente', 'info');
            setTimeout(() => {
                window.location.href = '/';
            }, 600);
        }
    } catch (err) {
        console.error('Error al cerrar sesión:', err);
    }
}

// Formatear pesos colombianos
function formatCOP(valor) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        maximumFractionDigits: 0
    }).format(valor);
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    CartManager.updateCounter();
    checkAuthStatus();

    // Toggle de perfil de usuario
    const profileBtn = document.getElementById('user-profile-btn');
    const userDropdown = document.getElementById('user-dropdown');
    if (profileBtn && userDropdown) {
        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('hidden');
        });
        document.addEventListener('click', () => {
            userDropdown.classList.add('hidden');
        });
    }

    // Toggle menú móvil
    const mobileBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileBtn && mobileMenu) {
        mobileBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }
});
