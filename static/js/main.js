(() => {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const spaced = (n) => Math.round(n).toLocaleString("ru-RU").replace(/,/g, " ");

  /* Header: scroll holati va mobil menyu */
  const header = $("[data-header]");
  if (header) {
    const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 10);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  const burger = $("[data-burger]");
  const nav = $("[data-nav]");
  if (burger && nav) {
    burger.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      burger.setAttribute("aria-expanded", String(open));
    });
    $$("a", nav).forEach((a) => a.addEventListener("click", () => {
      nav.classList.remove("is-open");
      burger.setAttribute("aria-expanded", "false");
    }));
  }

  /* Xabarlar (toast) — 6 soniyadan keyin yopiladi */
  $$(".toast").forEach((toast) => {
    const hide = () => {
      toast.classList.add("is-hiding");
      setTimeout(() => toast.remove(), 300);
    };
    $("[data-toast-close]", toast)?.addEventListener("click", hide);
    setTimeout(hide, 6000);
  });

  /* Telefon maskasi: +998 90 123 45 67 */
  $$("[data-phone-mask]").forEach((input) => {
    const format = () => {
      let digits = input.value.replace(/\D/g, "");
      if (!digits.startsWith("998")) digits = "998" + digits.replace(/^998/, "");
      digits = digits.slice(0, 12);
      const parts = [digits.slice(3, 5), digits.slice(5, 8), digits.slice(8, 10), digits.slice(10, 12)].filter(Boolean);
      input.value = "+998" + (parts.length ? " " + parts.join(" ") : " ");
    };
    input.addEventListener("focus", () => { if (!input.value) input.value = "+998 "; });
    input.addEventListener("input", format);
    input.addEventListener("blur", () => { if (input.value.replace(/\D/g, "") === "998") input.value = ""; });
    if (input.value) format();
  });

  /* Katalog filtrlari: radio/select o'zgarsa darhol yuboriladi */
  $$("[data-autosubmit]").forEach((form) => {
    $$("input[type=radio], select", form).forEach((el) =>
      el.addEventListener("change", () => form.requestSubmit())
    );
  });

  /* Galereya */
  const gallery = $("[data-gallery]");
  if (gallery) {
    const main = $("[data-gallery-main]", gallery);
    $$("[data-gallery-src]", gallery).forEach((thumb) => {
      thumb.addEventListener("click", () => {
        $$(".gallery__thumb", gallery).forEach((t) => t.classList.remove("is-active"));
        thumb.classList.add("is-active");
        main.innerHTML = `<img class="car-visual car-visual--hero" src="${thumb.dataset.gallerySrc}" alt="">`;
      });
    });
  }

  /* Rang tanlash: SVG siluet rangini o'zgartiradi */
  const colors = $("[data-colors]");
  if (colors) {
    const label = $("[data-color-name]", colors);
    const hero = colors.closest(".car-hero");
    $$("[data-color]", colors).forEach((btn) => {
      btn.addEventListener("click", () => {
        $$(".swatch", colors).forEach((s) => s.classList.remove("is-active"));
        btn.classList.add("is-active");
        label.textContent = btn.dataset.name;
        $$("svg.car-visual", hero).forEach((svg) => svg.style.setProperty("--car", btn.dataset.color));
      });
    });
  }

  /* Kredit kalkulyatori (annuitet) */
  const credit = $("[data-credit]");
  if (credit) {
    const price = Number(credit.dataset.price);
    const yearlyRate = Number(credit.dataset.rate);
    const usd = Number(credit.dataset.usd);
    const down = $("[data-credit-down]", credit);
    const downLabel = $("[data-credit-down-label]", credit);
    const monthlyEl = $("[data-credit-monthly]", credit);
    const loanEl = $("[data-credit-loan]", credit);
    const message = $("[data-credit-message]", credit);

    const calc = () => {
      const downPct = Number(down.value);
      const months = Number($("input[name=credit-term]:checked", credit).value);
      const loan = price * (1 - downPct / 100);
      const r = yearlyRate / 12 / 100;
      const monthly = r ? (loan * r) / (1 - Math.pow(1 + r, -months)) : loan / months;

      downLabel.textContent = `${downPct}% · $${spaced(price * downPct / 100)}`;
      monthlyEl.textContent = `$${spaced(monthly)}`;
      monthlyEl.title = `≈ ${spaced(monthly * usd)} so'm`;
      loanEl.textContent = `$${spaced(loan)}`;
      message.value =
        `Kredit hisob-kitobi: boshlang'ich to'lov ${downPct}% ($${spaced(price * downPct / 100)}), ` +
        `muddat ${months} oy, oylik to'lov ~$${spaced(monthly)} (≈ ${spaced(monthly * usd)} so'm).`;
    };

    credit.addEventListener("input", calc);
    calc();
  }
})();
