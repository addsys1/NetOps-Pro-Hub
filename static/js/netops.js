'use strict';

/* ── Clipboard helpers ──────────────────────────────────────── */

function copyCode(btn) {
  const block = btn.closest('.command-block-full');
  if (!block) return;
  const pre = block.querySelector('pre');
  if (!pre) return;
  _writeToClipboard(pre.innerText, btn);
}

function copyAllCommands() {
  const blocks = document.querySelectorAll('.generated-cmd');
  if (!blocks.length) return;
  const allText = Array.from(blocks)
    .map(b => b.getAttribute('data-cmd') || b.innerText)
    .join('\n!\n');
  const btn = document.querySelector('[data-action="copy-all"]');
  _writeToClipboard(allText.trim(), btn);
}

function _writeToClipboard(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    _flashCopied(btn);
  }).catch(() => {
    _fallbackCopy(text);
    if (btn) _flashCopied(btn);
  });
}

function _flashCopied(btn) {
  if (!btn) return;
  const original = btn.innerHTML;
  btn.innerHTML = '<i class="bi bi-check2 me-1"></i>Copié !';
  btn.classList.add('copied');
  setTimeout(() => {
    btn.innerHTML = original;
    btn.classList.remove('copied');
  }, 2000);
}

function _fallbackCopy(text) {
  const el = document.createElement('textarea');
  el.value = text;
  Object.assign(el.style, { position: 'fixed', opacity: '0', top: '0', left: '0' });
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);
}

/* ── DOMContentLoaded ───────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {

  /* Auto-submit filter form on select change */
  const filterForm = document.getElementById('filterForm');
  if (filterForm) {
    filterForm.querySelectorAll('select').forEach(sel => {
      sel.addEventListener('change', () => filterForm.submit());
    });
  }

  /* Bootstrap Tooltips */
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el, { trigger: 'hover' });
  });

  /* Smooth scroll for TOC links */
  document.querySelectorAll('.toc-link[data-target]').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const target = document.getElementById(link.dataset.target);
      if (target) {
        const offset = 80;
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  /* Highlight active TOC link on scroll */
  const tocLinks = document.querySelectorAll('.toc-link[data-target]');
  if (tocLinks.length) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          tocLinks.forEach(l => l.classList.toggle('active', l.dataset.target === id));
        }
      });
    }, { rootMargin: '-80px 0px -60% 0px', threshold: 0 });

    tocLinks.forEach(l => {
      const el = document.getElementById(l.dataset.target);
      if (el) observer.observe(el);
    });
  }

  /* Generator: show results tab automatically after submit */
  const genResults = document.getElementById('generatedContent');
  if (genResults) {
    const firstTab = document.querySelector('#genTabs .nav-link:not([disabled])');
    if (firstTab) firstTab.click();
  }

});
