(() => {
  const boardElement = document.getElementById('board');
  const statusText = document.getElementById('statusText');
  const resetBtn = document.getElementById('resetBtn');
  const scoresList = document.getElementById('scoresList');

  const WIN_LINES = [
    [0,1,2],[3,4,5],[6,7,8],
    [0,3,6],[1,4,7],[2,5,8],
    [0,4,8],[2,4,6]
  ];

  let board = Array(9).fill('');
  let current = 'X';
  let ended = false;
  let moveCount = 0;
  let startTs = performance.now();

  function setStatus(text) {
    statusText.textContent = text;
  }

  function winnerOf(b) {
    for (const [a, c, d] of WIN_LINES) {
      if (b[a] && b[a] === b[c] && b[a] === b[d]) return b[a];
    }
    return null;
  }

  function handleClickCell(evt) {
    const btn = evt.target.closest('.cell');
    if (!btn) return;
    const idx = Number(btn.dataset.idx);
    if (ended || board[idx]) return;

    board[idx] = current;
    btn.textContent = current;
    moveCount += 1;

    const w = winnerOf(board);
    if (w) {
      ended = true;
      setStatus(`${w} 获胜！`);
      submitScore('win');
      return;
    }
    if (board.every(Boolean)) {
      ended = true;
      setStatus('平局');
      submitScore('draw');
      return;
    }
    current = current === 'X' ? 'O' : 'X';
    setStatus(`轮到 ${current}`);
  }

  function resetGame() {
    board = Array(9).fill('');
    current = 'X';
    ended = false;
    moveCount = 0;
    startTs = performance.now();
    for (const btn of boardElement.querySelectorAll('.cell')) {
      btn.textContent = '';
    }
    setStatus('轮到 X');
  }

  async function fetchScores() {
    try {
      const res = await fetch('/api/scores');
      const data = await res.json();
      const scores = data.scores || [];
      scoresList.innerHTML = '';
      for (const s of scores) {
        const li = document.createElement('li');
        li.textContent = `${s.created_at} - ${s.player} ${s.result} - ${s.moves}步 ${s.duration_ms}ms`;
        scoresList.appendChild(li);
      }
    } catch (e) {
      // ignore for demo
    }
  }

  async function submitScore(result) {
    const duration = Math.max(0, Math.round(performance.now() - startTs));
    try {
      await fetch('/api/scores', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player: 'Player', result, moves: moveCount, duration_ms: duration }),
      });
      fetchScores();
    } catch (e) {
      // ignore for demo
    }
  }

  boardElement.addEventListener('click', handleClickCell);
  resetBtn.addEventListener('click', resetGame);
  fetchScores();
})();

