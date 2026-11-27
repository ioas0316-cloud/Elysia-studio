/**
 * Elysia World-Tree Online Cognitive Virtual World Client (/world-tree)
 */
(function initWorldTree() {
  'use strict';

  const canvas = document.getElementById('worldCanvas');
  const ctx = canvas ? canvas.getContext('2d') : null;
  let world = null;
  let ledgerSummary = null;
  let t = 0;

  function resize() {
    if (!canvas || !ctx) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.max(320, Math.floor(rect.width * dpr));
    canvas.height = Math.max(320, Math.floor(rect.height * dpr));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  window.addEventListener('resize', resize);
  resize();

  async function postAction(payload) {
    try {
      const resp = await fetch('/api/world-tree/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (resp.ok && data.world) {
        world = data.world;
        renderPanels();
      }
    } catch {}
  }

  async function poll() {
    try {
      const resp = await fetch('/api/world-tree/state');
      const data = await resp.json();
      if (resp.ok && data.world) {
        world = data.world;
        ledgerSummary = data.ledger_summary;
        renderPanels();
      }
    } catch {}
  }

  function escapeHtml(s) {
    return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function renderPanels() {
    if (!world) return;
    const dBadge = document.getElementById('deltaBadge');
    if (dBadge) dBadge.textContent = `64b 델타 패킷: ${world.lastDeltaPacketBytes} B/tick`;

    const hudR = document.getElementById('hudRight');
    if (hudR) hudR.textContent = `열매 공유: ${world.fruitsShared} · 마찰: ${world.frictionEvents} · CoW 가지: ${world.cowBranches}`;

    const sBox = document.getElementById('summaryBox');
    if (sBox) {
      const raw = ledgerSummary ? ledgerSummary.raw_absorbed : 0;
      const ice = ledgerSummary ? ledgerSummary.ice_symbols : 0;
      const cmp = ledgerSummary ? ledgerSummary.compounds : 0;
      sBox.textContent = `틱 #${world.tick} · 노드 ${world.agents.length} · 원장 연결(원시 ${raw} → 얼음 ${ice} · 분자 ${cmp})`;
    }

    const aList = document.getElementById('agentList');
    if (aList) {
      aList.innerHTML = world.agents
        .map(
          (a) =>
            `<div><strong>${escapeHtml(a.name)}</strong> (${Math.round(a.energy * 100)}%) · ${escapeHtml(a.status)} <span class="mono" style="font-size:10px;">[${escapeHtml(a.word64)}]</span></div>`
        )
        .join('');
    }

    const eList = document.getElementById('eventList');
    if (eList) {
      eList.innerHTML = (world.events || [])
        .map((e) => `<div><span class="mono" style="font-size:10px;">${escapeHtml(e.at.slice(11))}</span> ${escapeHtml(e.text)}</div>`)
        .join('');
    }
  }

  function draw() {
    t += 0.02;
    if (ctx && canvas) {
      const rect = canvas.parentElement.getBoundingClientRect();
      const W = rect.width;
      const H = rect.height;
      const cx = W * 0.5;
      const cy = H * 0.5;
      ctx.clearRect(0, 0, W, H);

      // World-Tree concentric resonance rings (0_value trunk)
      [0.14, 0.27, 0.40].forEach((rFrac, i) => {
        ctx.strokeStyle = i === 0 ? 'rgba(16,185,129,0.28)' : 'rgba(6,182,212,0.16)';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(cx, cy, Math.min(W, H) * rFrac + Math.sin(t + i) * 3, 0, Math.PI * 2);
        ctx.stroke();
      });

      // Trunk core glow
      ctx.fillStyle = 'rgba(16, 185, 129, 0.22)';
      ctx.beginPath();
      ctx.arc(cx, cy, 24 + Math.sin(t * 2) * 3, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#10B981';
      ctx.font = '11px "IBM Plex Mono", monospace';
      ctx.fillText('세계수 중심축 (0_value)', cx - 64, cy + 38);

      if (world) {
        const byId = {};
        world.agents.forEach((a) => { byId[a.id] = a; });

        // Draw Resonance & Friction Beams
        (world.beams || []).forEach((b) => {
          const a = byId[b.from];
          const c = byId[b.to];
          if (!a || !c) return;
          ctx.strokeStyle = b.kind === 'friction' ? 'rgba(244, 63, 94, 0.78)' : 'rgba(6, 182, 212, 0.52)';
          ctx.lineWidth = b.kind === 'friction' ? 2.4 : 1.6;
          ctx.beginPath();
          ctx.moveTo(a.x * W, a.y * H);
          ctx.lineTo(c.x * W, c.y * H);
          ctx.stroke();
        });

        // Draw Shared Principle Fruits
        (world.fruits || []).forEach((f) => {
          const fx = f.x * W;
          const fy = f.y * H;
          ctx.fillStyle = '#F59E0B';
          ctx.beginPath();
          ctx.arc(fx, fy, 4.5, 0, Math.PI * 2);
          ctx.fill();
          ctx.fillStyle = 'rgba(254, 243, 199, 0.8)';
          ctx.font = '10px "IBM Plex Sans", sans-serif';
          ctx.fillText(f.label, fx + 7, fy + 3);
        });

        // Draw Branch Agents & Human Avatar
        world.agents.forEach((a) => {
          const ax = a.x * W;
          const ay = a.y * H;
          const col = a.role === 'human' ? '#F59E0B' : a.role === 'selfish' ? '#F43F5E' : '#06B6D4';
          const rad = a.role === 'human' ? 11 : 8.5;
          ctx.fillStyle = col;
          ctx.beginPath();
          ctx.arc(ax, ay, rad, 0, Math.PI * 2);
          ctx.fill();
          ctx.strokeStyle = '#F1F5F9';
          ctx.lineWidth = 1.2;
          ctx.stroke();
          ctx.fillStyle = '#F1F5F9';
          ctx.font = '11px "IBM Plex Sans", sans-serif';
          ctx.fillText(a.name, ax + 13, ay + 4);
        });
      }
    }
    window.requestAnimationFrame(draw);
  }

  canvas?.addEventListener('click', (ev) => {
    const rect = canvas.getBoundingClientRect();
    const x = (ev.clientX - rect.left) / rect.width;
    const y = (ev.clientY - rect.top) / rect.height;
    postAction({ kind: 'move_user', x, y });
  });

  document.getElementById('btnPlantFruit')?.addEventListener('click', () => {
    const inp = document.getElementById('fruitInput');
    const label = (inp?.value || '').trim() || '상보 공명 열매';
    if (inp) inp.value = '';
    postAction({ kind: 'plant_fruit', label });
  });
  document.getElementById('btnSpawnSelfish')?.addEventListener('click', () => postAction({ kind: 'spawn_selfish' }));
  document.getElementById('btnHealSelfish')?.addEventListener('click', () => postAction({ kind: 'heal_selfish' }));
  document.getElementById('btnForkCow')?.addEventListener('click', () => postAction({ kind: 'fork_cow_branch' }));

  poll();
  window.setInterval(poll, 900);
  window.requestAnimationFrame(draw);
})();
