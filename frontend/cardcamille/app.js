(() => {
  const csvInput = document.getElementById('csvInput');
  const renderBtn = document.getElementById('renderCards');
  const clearBtn = document.getElementById('clearCards');
  const livePreviewCheckbox = document.getElementById('livePreview');
  const cardsContainer = document.getElementById('cardsContainer');
  const cardCount = document.getElementById('cardCount');
  const cardTemplate = document.getElementById('cardTemplate');
  const prevCardBtn = document.getElementById('prevCard');
  const nextCardBtn = document.getElementById('nextCard');
  const flipCardBtn = document.getElementById('flipCard');
  const statusMessage = document.getElementById('statusMessage');

  if (!csvInput || !renderBtn || !clearBtn || !livePreviewCheckbox || !cardsContainer || !cardCount || !cardTemplate || !prevCardBtn || !nextCardBtn || !flipCardBtn) {
    // Bail out silently if the DOM is not ready.
    return;
  }

  let lastFileName = '';
  let lastParseResult = { headers: [], records: [] };
  let cardsData = [];
  let currentCardIndex = 0;
  let isCardFlipped = false;

  setStatus('Aucun fichier importé pour le moment.');
  updateCardCount(0);
  renderPlaceholder('Importez un fichier CSV pour afficher vos cartes ici.');
  updateNavigationState();
  updateFlipButtonLabel();
  toggleRenderButton();

  csvInput.addEventListener('change', async (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      setStatus('Veuillez sélectionner un fichier CSV.');
      return;
    }

    try {
      const text = await readFile(file);
      const result = parseCsv(text);
      lastFileName = file.name;
      lastParseResult = result;

      if (!result.records.length) {
        setStatus(`Le fichier « ${file.name} » ne contient aucune ligne exploitable.`, 'warning');
        clearCards();
        return;
      }

      setStatus(`Import réussi : ${result.records.length} carte(s) depuis « ${file.name} ».`, 'success');
      toggleRenderButton();

      if (livePreviewCheckbox.checked) {
        renderCards(result.records, result.headers);
      } else {
        resetCardState();
        renderPlaceholder('Cliquez sur « Afficher les cartes » pour voir vos cartes.');
      }
    } catch (error) {
      console.error(error);
      setStatus(error instanceof Error ? error.message : 'Échec de la lecture du fichier CSV.', 'error');
    }
  });

  renderBtn.addEventListener('click', () => {
    if (!lastParseResult.records.length) {
      setStatus("Importez un fichier CSV avant d'afficher les cartes.", 'warning');
      return;
    }

    renderCards(lastParseResult.records, lastParseResult.headers);
  });

  clearBtn.addEventListener('click', () => {
    clearCards();
    csvInput.value = '';
    lastParseResult = { headers: [], records: [] };
    lastFileName = '';
    toggleRenderButton();
    setStatus('Cartes effacées. Importez un nouveau fichier pour recommencer.');
  });

  livePreviewCheckbox.addEventListener('change', () => {
    toggleRenderButton();

    if (livePreviewCheckbox.checked && lastParseResult.records.length) {
      renderCards(lastParseResult.records, lastParseResult.headers);
      setStatus(`Aperçu automatique activé pour « ${lastFileName || 'votre fichier'} ».`, 'success');
    } else if (!livePreviewCheckbox.checked) {
      setStatus('Aperçu automatique désactivé. Cliquez sur « Afficher les cartes » après un import.');
    }
  });

  prevCardBtn.addEventListener('click', goToPreviousCard);
  nextCardBtn.addEventListener('click', goToNextCard);
  flipCardBtn.addEventListener('click', () => flipCurrentCard());

  cardsContainer.addEventListener('click', (event) => {
    if (!cardsData.length) {
      return;
    }

    if (!event.target.closest('.card-flip')) {
      return;
    }

    flipCurrentCard();
  });

  document.addEventListener('keydown', handleKeyboardNavigation);

  function readFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onerror = () => reject(new Error('Impossible de lire le fichier sélectionné.'));
      reader.onload = () => {
        if (typeof reader.result !== 'string') {
          reject(new Error('Format de fichier inattendu.'));
          return;
        }

        resolve(reader.result);
      };
      reader.readAsText(file, 'utf-8');
    });
  }

  function parseCsv(text) {
    if (!text || !text.trim()) {
      return { headers: [], records: [] };
    }

    const normalised = text.replace(/\r\n?/g, '\n');
    const delimiter = detectDelimiter(normalised);
    const rows = [];
    const currentRow = [];
    let currentValue = '';
    let inQuotes = false;

    const pushValue = () => {
      currentRow.push(currentValue.trim());
      currentValue = '';
    };

    const pushRow = () => {
      // Avoid pushing empty trailing rows
      if (currentRow.length === 1 && currentRow[0] === '') {
        currentRow.length = 0;
        return;
      }
      rows.push([...currentRow]);
      currentRow.length = 0;
    };

    for (let index = 0; index < normalised.length; index += 1) {
      const char = normalised[index];

      if (char === '"') {
        if (inQuotes && normalised[index + 1] === '"') {
          currentValue += '"';
          index += 1;
        } else {
          inQuotes = !inQuotes;
        }
        continue;
      }

      if (char === delimiter && !inQuotes) {
        pushValue();
        continue;
      }

      if (char === '\n' && !inQuotes) {
        pushValue();
        pushRow();
        continue;
      }

      currentValue += char;
    }

    // Flush remaining buffered value/row
    pushValue();
    if (currentRow.length) {
      pushRow();
    }

    if (!rows.length) {
      return { headers: [], records: [] };
    }

    const headers = rows[0].map((header, index) => {
      const label = header.trim();
      return label || `col_${index + 1}`;
    });

    if (!headers.some((header) => header && header.trim().length)) {
      throw new Error('Impossible de déterminer les en-têtes dans le fichier CSV.');
    }

    const records = rows.slice(1)
      .filter((row) => row.some((cell) => cell && cell.trim().length))
      .map((row) => {
        const record = {};
        headers.forEach((header, index) => {
          record[header] = row[index] ?? '';
        });
        return record;
      });

    return { headers, records };
  }

  function detectDelimiter(sample) {
    const firstLineEnd = sample.indexOf('\n');
    const firstLine = firstLineEnd === -1 ? sample : sample.slice(0, firstLineEnd);
    const delimiters = [',', ';', '\t'];

    const scores = delimiters.map((delimiter) => {
      let score = 0;
      let inQuotes = false;

      for (let i = 0; i < firstLine.length; i += 1) {
        const char = firstLine[i];
        if (char === '"') {
          inQuotes = !inQuotes;
          continue;
        }
        if (char === delimiter && !inQuotes) {
          score += 1;
        }
      }
      return { delimiter, score };
    });

    scores.sort((a, b) => b.score - a.score);
    return scores[0].score > 0 ? scores[0].delimiter : ',';
  }

  function renderCards(records, headers) {
    const fieldMap = computeFieldMap(headers);

    cardsData = records.map((record, index) => {
      const position = index + 1;
      const reference = normaliseCell(record[fieldMap.reference]) || `REF-${position}`;
      const title = normaliseCell(record[fieldMap.title]) || `Carte ${position}`;
      const description = normaliseCell(record[fieldMap.description]);

      return { reference, title, description };
    });

    if (!cardsData.length) {
      resetCardState();
      renderPlaceholder('Le fichier importé ne contient aucune carte exploitable.');
      toggleRenderButton();
      return;
    }

    currentCardIndex = 0;
    isCardFlipped = false;
    renderActiveCard();
    toggleRenderButton();
  }

  function renderActiveCard() {
    if (!cardsData.length) {
      renderPlaceholder('Aucune carte à afficher. Importez un fichier CSV pour commencer.');
      updateCardCount(0);
      updateNavigationState();
      updateFlipButtonLabel();
      return;
    }

    const card = cardsData[currentCardIndex];
    const node = cardTemplate.content.firstElementChild.cloneNode(true);
    const inner = node.querySelector('.card-flip__inner');
    const referenceFront = node.querySelector('.card-reference--front');
    const titleFront = node.querySelector('.card-title--front');
    const hint = node.querySelector('.card-hint');
    const referenceBack = node.querySelector('.card-reference--back');
    const titleBack = node.querySelector('.card-title--back');
    const descriptionNode = node.querySelector('.card-description');

    referenceFront.textContent = card.reference;
    titleFront.textContent = card.title;
    referenceBack.textContent = card.reference;
    titleBack.textContent = card.title;

    if (card.description) {
      descriptionNode.textContent = card.description;
      descriptionNode.classList.remove('card-description--empty');
      if (hint) {
        hint.textContent = 'Cliquez sur la carte ou utilisez « Retourner la carte » pour voir la description.';
      }
    } else {
      descriptionNode.textContent = 'Aucune description fournie pour cette carte.';
      descriptionNode.classList.add('card-description--empty');
      if (hint) {
        hint.textContent = 'Cette carte ne possède pas de description détaillée.';
      }
    }

    inner.classList.toggle('is-flipped', isCardFlipped);

    cardsContainer.innerHTML = '';
    cardsContainer.appendChild(node);

    updateCardCount(cardsData.length);
    updateNavigationState();
    updateFlipButtonLabel();
  }

  function computeFieldMap(headers) {
    const normalised = headers.map((header) => header.toLowerCase());

    const findHeader = (candidates, fallbackIndex = 0) => {
      for (const candidate of candidates) {
        const index = normalised.indexOf(candidate);
        if (index !== -1) {
          return headers[index];
        }
      }
      return headers[fallbackIndex] ?? headers[0];
    };

    return {
      reference: findHeader(['reference', 'ref', 'référence', 'id', 'code'], 0),
      title: findHeader(['title', 'titre', 'name', 'nom'], Math.min(1, headers.length - 1)),
      description: findHeader(['description', 'desc', 'texte', 'text', 'details'], Math.min(2, headers.length - 1)),
    };
  }

  function normaliseCell(value) {
    if (value === undefined || value === null) {
      return '';
    }
    return String(value).trim();
  }

  function clearCards() {
    resetCardState();
    renderPlaceholder('Importez un fichier CSV pour afficher vos cartes ici.');
  }

  function resetCardState() {
    cardsData = [];
    currentCardIndex = 0;
    isCardFlipped = false;
    updateNavigationState();
    updateFlipButtonLabel();
    updateCardCount(0);
  }

  function renderPlaceholder(message) {
    cardsContainer.innerHTML = `
      <div class="card-placeholder">
        <p>${message}</p>
      </div>
    `;
  }

  function updateCardCount(total) {
    if (!total) {
      cardCount.textContent = '0 carte';
      return;
    }

    cardCount.textContent = `Carte ${currentCardIndex + 1} / ${total}`;
  }

  function setStatus(message, variant = 'info') {
    statusMessage.textContent = message;
    statusMessage.dataset.variant = variant;
  }

  function toggleRenderButton() {
    const hasRecords = lastParseResult.records.length > 0;
    renderBtn.disabled = livePreviewCheckbox.checked || !hasRecords;
    renderBtn.title = renderBtn.disabled
      ? "Désactivez l'aperçu automatique pour utiliser ce bouton."
      : '';
  }

  function goToCard(targetIndex) {
    if (!cardsData.length) {
      return;
    }

    const clamped = Math.max(0, Math.min(targetIndex, cardsData.length - 1));
    if (clamped === currentCardIndex) {
      return;
    }

    currentCardIndex = clamped;
    isCardFlipped = false;
    renderActiveCard();
  }

  function goToPreviousCard() {
    goToCard(currentCardIndex - 1);
  }

  function goToNextCard() {
    goToCard(currentCardIndex + 1);
  }

  function flipCurrentCard(forceState) {
    if (!cardsData.length) {
      return;
    }

    if (typeof forceState === 'boolean') {
      isCardFlipped = forceState;
    } else {
      isCardFlipped = !isCardFlipped;
    }

    const inner = cardsContainer.querySelector('.card-flip__inner');
    if (inner) {
      inner.classList.toggle('is-flipped', isCardFlipped);
    }
    updateFlipButtonLabel();
  }

  function updateNavigationState() {
    const total = cardsData.length;
    const disablePrev = total <= 1 || currentCardIndex === 0;
    const disableNext = total <= 1 || currentCardIndex >= total - 1;

    prevCardBtn.disabled = total === 0 || disablePrev;
    nextCardBtn.disabled = total === 0 || disableNext;
  }

  function updateFlipButtonLabel() {
    if (!cardsData.length) {
      flipCardBtn.disabled = true;
      flipCardBtn.textContent = 'Retourner la carte';
      flipCardBtn.title = 'Importez des cartes pour activer ce bouton.';
      return;
    }

    const currentCard = cardsData[currentCardIndex];
    const hasDescription = Boolean(currentCard.description);

    flipCardBtn.disabled = false;
    flipCardBtn.textContent = isCardFlipped ? 'Revenir à la carte' : hasDescription ? 'Voir la description' : 'Retourner la carte';
    flipCardBtn.title = hasDescription
      ? 'Affichez ou masquez la description de cette carte.'
      : 'Cette carte ne possède pas de description détaillée.';
  }

  function handleKeyboardNavigation(event) {
    if (!cardsData.length || event.defaultPrevented) {
      return;
    }

    const activeElement = document.activeElement;
    if (activeElement) {
      const tagName = activeElement.tagName;
      if (['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON'].includes(tagName)) {
        return;
      }
      if (activeElement.isContentEditable) {
        return;
      }
    }

    if (event.key === 'ArrowRight') {
      event.preventDefault();
      goToNextCard();
    } else if (event.key === 'ArrowLeft') {
      event.preventDefault();
      goToPreviousCard();
    } else if (event.key === ' ' || event.key === 'Spacebar') {
      event.preventDefault();
      flipCurrentCard();
    }
  }
})();
