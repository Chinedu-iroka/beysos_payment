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
function isInCart(id) { return cartLoad().some(function(i) { return i.id === id; }); }

function cartAdd(item) {
  var c = cartLoad();
  if (!c.find(function(i) { return i.id === item.id; })) {
    c.push(item);
    cartSave(c);
  }
  cartRenderAll();
}

function cartRemove(id) {
  cartSave(cartLoad().filter(function(i) { return String(i.id) !== String(id); }));

  // Reset gallery image button (id is a number)
  var btn  = document.getElementById('cart-btn-' + id);
  var card = document.getElementById('card-' + id);
  if (btn)  { btn.textContent = '+ Add to Cart'; btn.classList.remove('added'); }
  if (card) { card.classList.remove('in-cart'); }

  // Reset prompt button (id is like "prompt-123", so extract the number)
  var promptBtn = document.getElementById('prompt-cart-btn-' + String(id).replace('prompt-', ''));
  if (promptBtn) {
    promptBtn.textContent = '+ Cart';
    promptBtn.style.background = 'transparent';
    promptBtn.style.color = 'var(--gold)';
  }

  // Reset bundle button (id is like "bundle-123")
  var bundleBtn = document.getElementById('bundle-cart-btn-' + String(id).replace('bundle-', ''));
  if (bundleBtn) { bundleBtn.textContent = '+ Add Bundle to Cart'; bundleBtn.classList.remove('added'); }

  cartRenderAll();
}

function cartEmpty() {
  cartLoad().forEach(function(item) {
    var id = item.id;

    // Gallery image button
    var btn  = document.getElementById('cart-btn-' + id);
    var card = document.getElementById('card-' + id);
    if (btn)  { btn.textContent = '+ Add to Cart'; btn.classList.remove('added'); }
    if (card) { card.classList.remove('in-cart'); }

    // Prompt button
    var promptBtn = document.getElementById('prompt-cart-btn-' + String(id).replace('prompt-', ''));
    if (promptBtn) {
      promptBtn.textContent = '+ Cart';
      promptBtn.style.background = 'transparent';
      promptBtn.style.color = 'var(--gold)';
    }

    // Bundle button
    var bundleBtn = document.getElementById('bundle-cart-btn-' + String(id).replace('bundle-', ''));
    if (bundleBtn) { bundleBtn.textContent = '+ Add Bundle to Cart'; bundleBtn.classList.remove('added'); }
  });
  cartClear();
  cartRenderAll();
}

function cartTotal() {
  return cartLoad().reduce(function(sum, item) {
    return sum + (parseFloat(item.price) || 0);
  }, 0);
}

function cartTotalCents() {
  return cartLoad().reduce(function(sum, item) {
    return sum + (parseInt(item.price_cents) || 0);
  }, 0);
}

function cartRenderAll() {
  var cart  = cartLoad();
  var count = cart.length;
  var total = cartTotal();

  var badge = document.getElementById('cartBadge');
  if (badge) { badge.textContent = count; badge.classList.toggle('visible', count > 0); }

  var label = document.getElementById('cartCountLabel');
  if (label) label.textContent = count + ' item' + (count !== 1 ? 's' : '');

  var footer = document.getElementById('cartFooterCount');
  if (footer) footer.textContent = count + ' image' + (count !== 1 ? 's' : '');

  var totalEl = document.getElementById('cartTotal');
  if (totalEl) totalEl.textContent = '$' + total.toFixed(2);

  var proceedBtn = document.getElementById('proceedBtn');
  if (proceedBtn) proceedBtn.disabled = count === 0;

  var itemsEl = document.getElementById('cartItems');
  if (!itemsEl) return;

  if (count === 0) {
    itemsEl.innerHTML = '<div class="cart-empty"><div class="icon">🛒</div><p>Your cart is empty.<br/>Add images you\'d like to book.</p></div>';
    return;
  }

  itemsEl.innerHTML = '';
  cart.forEach(function(item) {
    var el = document.createElement('div');
    el.className = 'cart-item';
    el.innerHTML =
      (item.src && (item.src.endsWith('.mp4') || item.src.endsWith('.webm') || item.src.endsWith('.mov'))
  ? '<div class="cart-item-img" style="background:#1a0533;display:flex;align-items:center;justify-content:center;font-size:24px;">🎬</div>'
  : item.src
    ? '<img class="cart-item-img" src="' + item.src + '" alt="' + item.title + '"/>'
    : '<div class="cart-item-img" style="background:#1a0533;display:flex;align-items:center;justify-content:center;font-size:24px;">🖼️</div>'
) +
      '<div class="cart-item-info">' +
        '<div class="cat">' + item.category + '</div>' +
        '<div class="title">' + item.title + '</div>' +
        '<div class="item-price">$' + parseFloat(item.price).toFixed(2) + '</div>' +
      '</div>' +
     '<button class="cart-item-remove" onclick="cartRemove(\'' + item.id + '\')" title="Remove">&times;</button>';
    itemsEl.appendChild(el);
  });
}

function cartSyncPageButtons() {
  cartLoad().forEach(function(item) {
    var btn  = document.getElementById('cart-btn-' + item.id);
    var card = document.getElementById('card-' + item.id);
    if (btn)  { btn.textContent = 'In Cart'; btn.classList.add('added'); }
    if (card) { card.classList.add('in-cart'); }
  });
}

function toggleCart() {
  var drawer  = document.getElementById('cartDrawer');
  var overlay = document.getElementById('cartOverlay');
  if (!drawer) return;
  var isOpen = drawer.classList.toggle('open');
  overlay.classList.toggle('open', isOpen);
  document.body.style.overflow = isOpen ? 'hidden' : '';
}

function openCart() {
  var drawer  = document.getElementById('cartDrawer');
  var overlay = document.getElementById('cartOverlay');
  if (!drawer) return;
  drawer.classList.add('open');
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeCart() {
  var drawer  = document.getElementById('cartDrawer');
  var overlay = document.getElementById('cartOverlay');
  if (!drawer) return;
  drawer.classList.remove('open');
  overlay.classList.remove('open');
  document.body.style.overflow = '';
}

function proceedToBook(orderUrl) {
  var cart = cartLoad();
  if (cart.length === 0) return;

  // Check if all items are prompts
  var allPrompts = cart.every(function(i) { return i.type === 'prompt'; });
  if (allPrompts) {
    if (typeof openPromptCheckout === 'function') openPromptCheckout();
    return;
  }

  // Filter out prompt items for the order form — prompts will be emailed after payment
  var styles     = cart.map(function(i) { return i.category; }).filter(function(v, i, a) { return a.indexOf(v) === i; }).join(', ');
  var titles     = cart.map(function(i) { return i.title; }).join(', ');
  var totalCents = cartTotalCents();
  window.location.href = orderUrl +
    '?style='  + encodeURIComponent(styles) +
    '&notes='  + encodeURIComponent('Selected images: ' + titles) +
    '&count='  + cart.length +
    '&amount=' + totalCents +
    '&cart='   + encodeURIComponent(JSON.stringify(cart));
}

function bookNow(orderUrl, id, src, category, title, price, priceCents) {
  // this is where my order form reads it correctly
  cartEmpty();
  cartAdd({ id: id, src: src, title: title, category: category, price: price, price_cents: priceCents });
  window.location.href = orderUrl +
    '?style='  + encodeURIComponent(category) +
    '&notes='  + encodeURIComponent('Selected image: ' + title) +
    '&count=1' +
    '&amount=' + priceCents +
    '&cart='   + encodeURIComponent(JSON.stringify(cartLoad()));
}

function addToCart(id, src, title, category, price, priceCents) {
  if (isInCart(id)) { cartRemove(id); return; }
  cartAdd({ id: id, src: src, title: title, category: category, price: price, price_cents: priceCents });
  var btn  = document.getElementById('cart-btn-' + id);
  var card = document.getElementById('card-' + id);
  if (btn)  { btn.textContent = 'In Cart'; btn.classList.add('added'); }
  if (card) { card.classList.add('in-cart'); }
  cartRenderAll();
}

document.addEventListener('DOMContentLoaded', function() {
  cartRenderAll();
  cartSyncPageButtons();
});