// const CART_KEY = 'cos_virtual';

// function getCart() {
//     const cartStr = localStorage.getItem(CART_KEY);
//     return cartStr ? JSON.parse(cartStr) : {};
// }

// function saveCart(cart) {
//     localStorage.setItem(CART_KEY, JSON.stringify(cart));
//     updateCartCount(); 
// }

// function adaugaInCos(id, nume, pret, stoc) {
//     let cart = getCart();
    
//     if (cart[id]) {
//         if (cart[id].cantitate < stoc) {
//             cart[id].cantitate++;
//             alert(`Cantitatea pentru ${nume} a fost actualizata!`);
//         } else {
//             alert("Nu poți adăuga mai mult decât stocul disponibil!");
//             return; 
//         }
//     } else {
//         if (stoc > 0) {
//             cart[id] = {
//                 'nume': nume,
//                 'pret': parseFloat(pret),
//                 'cantitate': 1,
//                 'stoc': parseInt(stoc)
//             };
//             alert(`${nume} a fost adăugat în coș!`);
//         } else {
//             alert("Produsul nu este disponibil.");
//             return;
//         }
//     }
    
//     saveCart(cart);
// }

// function modificaCantitate(id, schimbare) {
//     let cart = getCart();
    
//     if (cart[id]) {
//         let nouaCantitate = cart[id].cantitate + schimbare;
        
//         if (nouaCantitate > cart[id].stoc) {
//             alert("Stoc insuficient!");
//             return;
//         }
        
//         if (nouaCantitate < 1) {
//             delete cart[id];
//         } else {
//             cart[id].cantitate = nouaCantitate;
//         }
        
//         saveCart(cart);
//         randeazaTabelCos();
//     }
// }

// function setCantitate(id, valoare) {
//     let cart = getCart();
//     valoare = parseInt(valoare);
    
//     if (cart[id]) {
//         if (valoare > cart[id].stoc) {
//             alert("Cantitatea depășește stocul!");
//             valoare = cart[id].stoc; 
//         } else if (valoare < 1) {
//             valoare = 1;
//         }
        
//         cart[id].cantitate = valoare;
//         saveCart(cart);
//         randeazaTabelCos();
//     }
// }

// function stergeProdus(id) {
//     let cart = getCart();
//     if (cart[id]) {
//         delete cart[id];
//         (cart);
//         rasaveCartndeazaTabelCos();
//     }
// }

// function golesteCos() {
//     localStorage.removeItem(CART_KEY);
//     randeazaTabelCos();
// }