// Funciones para el carrito de compras
function updateQuantity(productId, change) {
    const input = document.getElementById(`quantity-${productId}`);
    let quantity = parseInt(input.value) + change;
    
    if (quantity < 1) quantity = 1;
    
    input.value = quantity;
    updateCartItem(productId, quantity);
}

function updateCartItem(productId, quantity) {
    fetch('/update_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `product_id=${productId}&quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar totales
            document.getElementById('cart-total').textContent = `$${data.cart_total.toFixed(2)}`;
            document.getElementById('cart-count').textContent = data.cart_count;
            
            // Si estamos en la página del carrito, recargar para ver cambios
            if (window.location.pathname === '/cart') {
                location.reload();
            }
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al actualizar el carrito');
    });
}

function removeFromCart(productId) {
    if (confirm('¿Estás seguro de que quieres eliminar este producto del carrito?')) {
        fetch('/remove_from_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `product_id=${productId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar totales
                document.getElementById('cart-total').textContent = `$${data.cart_total.toFixed(2)}`;
                document.getElementById('cart-count').textContent = data.cart_count;
                
                // Eliminar elemento del DOM
                document.getElementById(`cart-item-${productId}`).remove();
                
                // Si el carrito está vacío, mostrar mensaje
                if (data.cart_count === 0) {
                    document.getElementById('cart-items').innerHTML = `
                        <div class="text-center py-5">
                            <h4>Tu carrito está vacío</h4>
                            <a href="/products" class="btn btn-purple mt-3">Seguir Comprando</a>
                        </div>
                    `;
                    document.getElementById('cart-summary').style.display = 'none';
                }
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar el producto del carrito');
        });
    }
}

// Inicialización cuando el documento está listo
document.addEventListener('DOMContentLoaded', function() {
    // Tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});