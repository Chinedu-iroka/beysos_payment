// PERSISTENT CART
// Stored in localStorage so it survives page navigation.
// Cleared only on successful payment or manual clear.

const CART_KEY = 'beysos_cart';

function cartLoad() {
  try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
  catch { return []; }
}
function cartSave(c) { localStorage.setItem(CART_KEY, JSON.stringify(c)); }
function cartClear() { localStorage.removeItem(CART_KEY); }
function isInCart(id) { return cartLoad().some(i => i.id === id); }

function cartAdd(item) {
  const c = cartLoad();
  if (!c.find(i => i.id === item.id)) { c.push(item); cartSave(c); }
  cartRenderAll();
}

function cartRemove(id) {
  cartSave(cartLoad().filter(i => i.id !== id));
  const btn  = document.getElementById('cart-btn-' + id);
  const card = document.getElementById('card-' + id);
  if (btn)  { btn.textContent = '+ Add to Cart'; btn.classList.remove('added'); }
  if (card) { card.classList.remove('in-cart'); }
  cartRenderAll();
}

function cartEmpty() {
  cartLoad().forEach(function(item) {
    const btn  = document.getElementById('cart-btn-' + item.id);
    const card = document.getElementById('card-' + item.id);
    if (btn)  { btn.textContent = '+ Add to Cart'; btn.classList.remove('added'); }
    if (card) { card.classList.remove('in-cart'); }
  });
  cartClear();
  cartRenderAll();
}

function cartRenderAll() {
  const cart  = cartLoad();
  const count = cart.length;

  const badge = document.getElementById('cartBadge');
  if (badge) { badge.textContent = count; badge.classList.toggle('visible', count > 0); }

  const label = document.getElementById('cartCountLabel');
  if (label) label.textContent = count + ' item' + (count !== 1 ? 's' : '');

  const footer = document.getElementById('cartFooterCount');
  if (footer) footer.textContent = count + ' image' + (count !== 1 ? 's' : '');

  const proceedBtn = document.getElementById('proceedBtn');
  if (proceedBtn) proceedBtn.disabled = count === 0;

  const itemsEl = document.getElementById('cartItems');
  if (!itemsEl) return;

  if (count === 0) {
    itemsEl.innerHTML = '<div class="cart-empty"><div class="icon">🛒</div><p>Your cart is empty.<br/>Add images you\'d like to book.</p></div>';
    return;
  }

  itemsEl.innerHTML = '';
  cart.forEach(function(item) {
    const el = document.createElement('div');
    el.className = 'cart-item';
    el.innerHTML =
      '<img class="cart-item-img" src="' + item.src + '" alt="' + item.title + '"/>' +
      '<div class="cart-item-info">' +
        '<div class="cat">' + item.category + '</div>' +
        '<div class="title">' + item.title + '</div>' +
      '</div>' +
      '<button class="cart-item-remove" onclick="cartRemove(' + item.id + ')" title="Remove">&times;</button>';
    itemsEl.appendChild(el);
  });
}

function cartSyncPageButtons() {
  cartLoad().forEach(function(item) {
    const btn  = document.getElementById('cart-btn-' + item.id);
    const card = document.getElementById('card-' + item.id);
    if (btn)  { btn.textContent = 'In Cart'; btn.classList.add('added'); }
    if (card) { card.classList.add('in-cart'); }
  });
}

function toggleCart() {
  const drawer  = document.getElementById('cartDrawer');
  const overlay = document.getElementById('cartOverlay');
  if (!drawer) return;
  const isOpen = drawer.classList.toggle('open');
  overlay.classList.toggle('open', isOpen);
  document.body.style.overflow = isOpen ? 'hidden' : '';
}

function openCart() {
  const drawer  = document.getElementById('cartDrawer');
  const overlay = document.getElementById('cartOverlay');
  if (!drawer) return;
  drawer.classList.add('open');
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeCart() {
  const drawer  = document.getElementById('cartDrawer');
  const overlay = document.getElementById('cartOverlay');
  if (!drawer) return;
  drawer.classList.remove('open');
  overlay.classList.remove('open');
  document.body.style.overflow = '';
}

function proceedToBook(orderUrl) {
  const cart = cartLoad();
  if (cart.length === 0) return;
  const styles = cart.map(function(i) { return i.category; }).filter(function(v, i, a) { return a.indexOf(v) === i; }).join(', ');
  const titles = cart.map(function(i) { return i.title; }).join(', ');
  window.location.href = orderUrl + '?style=' + encodeURIComponent(styles) + '&notes=' + encodeURIComponent('Selected images: ' + titles) + '&count=' + cart.length;
}

function bookNow(orderUrl, category, title) {
  window.location.href = orderUrl + '?style=' + encodeURIComponent(category) + '&notes=' + encodeURIComponent('Selected image: ' + title);
}

function addToCart(id, src, title, category) {
  if (isInCart(id)) { cartRemove(id); return; }
  cartAdd({ id: id, src: src, title: title, category: category });
  const btn  = document.getElementById('cart-btn-' + id);
  const card = document.getElementById('card-' + id);
  if (btn)  { btn.textContent = 'In Cart'; btn.classList.add('added'); }
  if (card) { card.classList.add('in-cart'); }
  openCart();
}

document.addEventListener('DOMContentLoaded', function() {
  cartRenderAll();
  cartSyncPageButtons();
});