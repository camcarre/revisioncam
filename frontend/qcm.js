(() => {
  const fileInput = document.getElementById('qcmCsvInput');
  const renderBtn = document.getElementById('renderQcm');
  const clearBtn = document.getElementById('clearQcm');
  const livePreview = document.getElementById('qcmLivePreview');
  const revealBtn = document.getElementById('revealAnswers');
  const statusNode = document.getElementById('qcmStatus');
  const qcmContainer = document.getElementById('qcmContainer');
  const qcmCount = document.getElementById('qcmCount');
  const summaryNode = document.getElementById('qcmSummary');
  const template = document.getElementById('qcmTemplate');

  if (!fileInput || !renderBtn || !clearBtn || !livePreview || !revealBtn || !statusNode || !qcmContainer || !qcmCount || !summaryNode || !template) {
    return;
  }

  let lastFileName = '';
  let lastParseResult = { headers: [], records: [] };
  let questionStates = [];
  let answerableQuestionCount = 0;
  let answersRevealed = false;

  setStatus('Importez un fichier CSV pour commencer.');
  updateCount(0);
  toggleRenderButton();
  resetRevealButton();
  updateSummaryProgress();

  // Fonction pour mélanger un tableau (algorithme Fisher-Yates)
  function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  fileInput.addEventListener('change', async (event) => {
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
        setStatus(`Le fichier « ${file.name} » ne contient aucune question.`, 'warning');
        clearDisplay();
        return;
      }

      setStatus(`Import réussi : ${result.records.length} question(s) depuis « ${file.name} ».`, 'success');
      toggleRenderButton();

      if (livePreview.checked) {
        renderQcm(result.records, result.headers);
      } else {
        clearDisplay();
      }
    } catch (error) {
      console.error(error);
      setStatus(error instanceof Error ? error.message : 'Échec de la lecture du fichier CSV.', 'error');
    }
  });

  renderBtn.addEventListener('click', () => {
    if (!lastParseResult.records.length) {
      setStatus("Importez un fichier CSV avant d'afficher les QCM.", 'warning');
      return;
    }

    renderQcm(lastParseResult.records, lastParseResult.headers);
  });

  clearBtn.addEventListener('click', () => {
    fileInput.value = '';
    lastFileName = '';
    lastParseResult = { headers: [], records: [] };
    clearDisplay();
    toggleRenderButton();
    setStatus('QCM effacés. Importez un nouveau fichier pour recommencer.');
  });

  revealBtn.addEventListener('click', () => {
    if (answersRevealed) {
      setStatus('Les réponses sont déjà affichées. Utilisez « Effacer » pour recommencer.', 'info');
      return;
    }

    if (!allQuestionsAnswered()) {
      const remaining = Math.max(answerableQuestionCount - countAnsweredQuestions(), 0);
      const suffix = remaining > 0 ? ` Il reste ${remaining} question(s).` : '';
      setStatus(`Répondez à toutes les questions avant d'afficher les réponses.${suffix}`, 'warning');
      return;
    }

    revealAnswers();
  });

  livePreview.addEventListener('change', () => {
    toggleRenderButton();

    if (livePreview.checked && lastParseResult.records.length) {
      renderQcm(lastParseResult.records, lastParseResult.headers);
      setStatus(`Aperçu automatique activé pour « ${lastFileName || 'votre fichier'} ».`, 'success');
    } else if (!livePreview.checked) {
      setStatus('Aperçu automatique désactivé. Cliquez sur « Afficher les QCM » après un import.');
    }
  });

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

  function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  function detectDelimiter(sample) {
    const firstLineEnd = sample.indexOf('\n');
    const firstLine = firstLineEnd === -1 ? sample : sample.slice(0, firstLineEnd);
    const delimiters = [',', ';', '\t'];

    const scores = delimiters.map((delimiter) => {
      let score = 0;
      let quotes = false;

      for (let i = 0; i < firstLine.length; i += 1) {
        const char = firstLine[i];
        if (char === '"') {
          quotes = !quotes;
          continue;
        }
        if (char === delimiter && !quotes) {
          score += 1;
        }
      }
      return { delimiter, score };
    });

    scores.sort((a, b) => b.score - a.score);
    return scores[0].score > 0 ? scores[0].delimiter : ',';
  }

  function renderQcm(records, headers) {
    qcmContainer.innerHTML = '';
    summaryNode.innerHTML = '';
    summaryNode.hidden = true;
    questionStates = [];
    answerableQuestionCount = 0;
    resetRevealButton();

    const fieldMap = computeFieldMap(headers);

    // Mélanger les questions après l'import
    const shuffledRecords = shuffleArray(records);

    shuffledRecords.forEach((record, index) => {
      const node = template.content.firstElementChild.cloneNode(true);
      const reference = (record[fieldMap.reference] || `QCM-${index + 1}`).trim();
      const question = (record[fieldMap.question] || `Question ${index + 1}`).trim();
      const correctValue = fieldMap.correct ? String(record[fieldMap.correct] ?? '') : '';
      const whyText = fieldMap.why ? String(record[fieldMap.why] ?? '').trim() : '';
      const choices = shuffleArray(fieldMap.choices
        .map((column) => ({
          column,
          label: record[column] ? String(record[column]).trim() : '',
        }))
        .filter((choice) => choice.label.length));

      const choiceList = node.querySelector('.qcm-choices');
      choiceList.innerHTML = '';

      const questionState = {
        index,
        reference,
        question,
        correctValue: correctValue.trim(),
        choices,
        choiceElements: [],
        selectedIndex: null,
        hasChoices: choices.length > 0,
        // footer supprimé dans la nouvelle structure HTML
      };

      if (!choices.length) {
        const emptyItem = document.createElement('li');
        emptyItem.textContent = 'Aucune réponse fournie dans ce CSV.';
        emptyItem.classList.add('qcm-choice', 'qcm-choice--empty');
        choiceList.appendChild(emptyItem);
      } else {
        answerableQuestionCount += 1;

        choices.forEach((choice, choiceIndex) => {
          const listItem = document.createElement('li');
          listItem.classList.add('qcm-choice');
          listItem.dataset.questionIndex = String(index);
          listItem.dataset.choiceIndex = String(choiceIndex);

          const marker = String.fromCharCode(65 + choiceIndex);
          const label = document.createElement('label');
          label.textContent = choice.label;

          const input = document.createElement('input');
          input.type = 'radio';
          input.name = `question-${index}`;
          input.value = choiceIndex;

          listItem.appendChild(input);
          listItem.appendChild(label);
          listItem.addEventListener('click', () => handleChoiceSelect(index, choiceIndex));

          choiceList.appendChild(listItem);

          questionState.choiceElements.push({ listItem, button: listItem });
        });
      }

      node.querySelector('.qcm-reference').textContent = reference;
      node.querySelector('.qcm-question').textContent = question;
      
      // Gérer la section "pourquoi" - masquée par défaut
      const whySection = node.querySelector('.qcm-why');
      const whyTextElement = node.querySelector('.qcm-why-text');
      if (whyText && whyText.length > 0) {
        whyTextElement.textContent = whyText;
        // Stocker le texte "pourquoi" dans l'état de la question
        questionState.whyText = whyText;
      }
      // Toujours masquer la section "pourquoi" au début
      whySection.style.display = 'none';
      
      // Footer supprimé dans la nouvelle structure HTML

      qcmContainer.appendChild(node);
      questionStates.push(questionState);
    });

    updateCount(records.length);
    toggleRenderButton();
    updateRevealButtonState();
    updateSummaryProgress();
  }

  function handleChoiceSelect(questionIndex, choiceIndex) {
    if (answersRevealed) {
      setStatus('Réinitialisez ou réimportez le questionnaire pour répondre à nouveau.', 'info');
      return;
    }

    const questionState = questionStates[questionIndex];

    if (!questionState || !questionState.hasChoices) {
      return;
    }

    const choiceEntry = questionState.choiceElements[choiceIndex];
    if (!choiceEntry) {
      return;
    }

    questionState.choiceElements.forEach(({ button }) => {
      button.classList.remove('selected');
    });

    choiceEntry.button.classList.add('selected');
    questionState.selectedIndex = choiceIndex;

    const answered = countAnsweredQuestions();

    if (answered < answerableQuestionCount) {
      const remaining = answerableQuestionCount - answered;
      setStatus(`${answered}/${answerableQuestionCount} question(s) répondues. Il reste ${remaining}.`, 'info');
    } else {
      setStatus('Toutes les questions ont une réponse. Cliquez sur « Afficher les réponses ».', 'success');
    }

    updateRevealButtonState();
    updateSummaryProgress();
  }

  function revealAnswers() {
    if (!questionStates.length) {
      setStatus("Importez un fichier CSV avant d'afficher les réponses.", 'warning');
      return;
    }

    if (answerableQuestionCount === 0) {
      setStatus('Ce questionnaire ne contient aucune réponse sélectionnable.', 'info');
      return;
    }

    let score = 0;
    let scorable = 0;

    questionStates.forEach((questionState) => {
      if (!questionState.hasChoices) {
        return;
      }

      const { choices, choiceElements, correctValue, selectedIndex, footer } = questionState;
      const hasCorrectValue = Boolean(correctValue && correctValue.trim().length);

      choiceElements.forEach(({ button }) => {
        button.classList.remove('correct', 'incorrect');
      });

      if (hasCorrectValue) {
        scorable += 1;
      }

      choiceElements.forEach(({ button }, idx) => {
        const choice = choices[idx];
        const isCorrect = isCorrectChoice(choice.label, choice.column, correctValue);

        if (isCorrect) {
          button.classList.add('correct');
        }

        if (selectedIndex === idx && !isCorrect && hasCorrectValue) {
          button.classList.add('incorrect');
        }
      });

      if (hasCorrectValue && selectedIndex !== null) {
        const selectedChoice = choices[selectedIndex];
        if (selectedChoice && isCorrectChoice(selectedChoice.label, selectedChoice.column, correctValue)) {
          score += 1;
        }
      }

      if (footer) {
        footer.innerHTML = '';
        if (hasCorrectValue) {
          const label = document.createElement('span');
          label.classList.add('qcm-correct-label');
          label.textContent = `Bonne réponse : ${correctValue.trim()}`;
          footer.appendChild(label);
        }

        if (selectedIndex !== null) {
          const selectedChoice = choices[selectedIndex];
          const answer = document.createElement('span');
          answer.classList.add('qcm-user-choice');
          answer.textContent = `Votre réponse : ${selectedChoice ? selectedChoice.label : '—'}`;
          footer.appendChild(answer);
        }
      }

      // Afficher la section "pourquoi" après révélation des réponses
      const questionNode = qcmContainer.children[questionState.index];
      if (questionNode) {
        const whySection = questionNode.querySelector('.qcm-why');
        if (whySection && questionState.whyText && questionState.whyText.length > 0) {
          whySection.style.display = 'block';
        }
      }
    });

    answersRevealed = true;
    revealBtn.disabled = true;
    revealBtn.textContent = 'Réponses affichées';
    revealBtn.title = 'Utilisez « Effacer » pour recommencer avec ce questionnaire.';

    renderSummaryResults(score, scorable);

    if (scorable > 0) {
      setStatus(`Score obtenu : ${score}/${scorable} question(s) correctes.`, 'success');
    } else {
      setStatus("Aucune réponse correcte n'a été définie dans ce questionnaire.", 'info');
    }
  }

  function countAnsweredQuestions() {
    return questionStates.reduce((total, question) => {
      if (!question.hasChoices) {
        return total;
      }
      return total + (question.selectedIndex !== null ? 1 : 0);
    }, 0);
  }

  function allQuestionsAnswered() {
    if (!answerableQuestionCount) {
      return false;
    }

    return questionStates.every((question) => {
      if (!question.hasChoices) {
        return true;
      }
      return question.selectedIndex !== null;
    });
  }

  function updateRevealButtonState() {
    const canReveal = !answersRevealed && answerableQuestionCount > 0 && allQuestionsAnswered();
    revealBtn.disabled = !canReveal;

    if (revealBtn.disabled) {
      revealBtn.title = answerableQuestionCount === 0
        ? 'Ce questionnaire ne contient aucune réponse sélectionnable.'
        : 'Répondez à toutes les questions pour afficher les réponses.';
    } else {
      revealBtn.title = '';
    }
  }

  function resetRevealButton() {
    answersRevealed = false;
    revealBtn.disabled = true;
    revealBtn.textContent = 'Afficher les réponses';
    revealBtn.title = 'Répondez à toutes les questions pour afficher les réponses.';
  }

  function updateSummaryProgress() {
    if (!questionStates.length) {
      summaryNode.hidden = true;
      summaryNode.textContent = '';
      return;
    }

    if (answersRevealed) {
      return;
    }

    if (answerableQuestionCount === 0) {
      summaryNode.hidden = false;
      summaryNode.textContent = 'Ce questionnaire ne comporte aucune réponse à sélectionner.';
      return;
    }

    const answered = countAnsweredQuestions();
    summaryNode.hidden = false;
    summaryNode.textContent = `${answered}/${answerableQuestionCount} question(s) répondues.`;
  }

  function renderSummaryResults(score, scorable) {
    const totalAnswered = countAnsweredQuestions();
    const totalQuestions = answerableQuestionCount;
    const percentage = scorable > 0 ? Math.round((score / scorable) * 100) : 0;
    const missingSolutions = Math.max(totalQuestions - scorable, 0);

    const fragments = [];

    if (scorable > 0) {
      fragments.push(`<p class="qcm-summary__score">Score : <strong>${score}/${scorable}</strong> (${percentage}%)</p>`);
    } else {
      fragments.push('<p class="qcm-summary__score">Score non calculé : aucune réponse correcte renseignée.</p>');
    }

    if (totalQuestions > 0) {
      fragments.push(`<p class="qcm-summary__detail">${totalAnswered}/${totalQuestions} question(s) répondues.</p>`);
    }

    if (missingSolutions > 0) {
      fragments.push(`<p class="qcm-summary__detail">${missingSolutions} question(s) sans bonne réponse définie.</p>`);
    }

    summaryNode.hidden = false;
    summaryNode.innerHTML = fragments.join('');
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

    const referenceHeader = findHeader(['reference', 'ref', 'référence', 'id', 'code'], 0);
    const questionHeader = findHeader(['question', 'titre', 'intitulé', 'prompt'], Math.min(1, headers.length - 1));

    let correctHeader = '';
    const correctCandidates = ['correct', 'bonne reponse', 'bonne réponse', 'answer', 'solution'];
    for (const candidate of correctCandidates) {
      const index = normalised.indexOf(candidate);
      if (index !== -1) {
        correctHeader = headers[index];
        break;
      }
    }

    let whyHeader = '';
    const whyCandidates = ['pourquoi', 'why', 'explication', 'raison'];
    for (const candidate of whyCandidates) {
      const index = normalised.indexOf(candidate);
      if (index !== -1) {
        whyHeader = headers[index];
        break;
      }
    }

    const excluded = new Set([referenceHeader, questionHeader, correctHeader, whyHeader].filter(Boolean));
    const choiceHeaders = headers.filter((header) => !excluded.has(header));

    return {
      reference: referenceHeader,
      question: questionHeader,
      correct: correctHeader,
      why: whyHeader,
      choices: choiceHeaders,
    };
  }

  function isCorrectChoice(choiceLabel, choiceHeader, correctValue) {
    if (!correctValue || !correctValue.trim()) {
      return false;
    }

    const normalisedChoice = choiceLabel.trim().toLowerCase();
    const normalisedHeader = choiceHeader.trim().toLowerCase();
    const normalisedCorrect = correctValue.trim().toLowerCase();

    if (!normalisedChoice) {
      return false;
    }

    if (normalisedCorrect === normalisedChoice) {
      return true;
    }

    if (normalisedCorrect === normalisedHeader) {
      return true;
    }

    const parts = normalisedCorrect.split('|').map((part) => part.trim()).filter(Boolean);
    if (parts.length > 1) {
      return parts.includes(normalisedChoice) || parts.includes(normalisedHeader);
    }

    return false;
  }

  function clearDisplay() {
    qcmContainer.innerHTML = '';
    summaryNode.innerHTML = '';
    summaryNode.hidden = true;
    questionStates = [];
    answerableQuestionCount = 0;
    resetRevealButton();
    updateSummaryProgress();
    updateCount(0);
  }

  function updateCount(total) {
    qcmCount.textContent = `${total} ${total > 1 ? 'questions' : 'question'}`;
  }

  function setStatus(message, variant = 'info') {
    statusNode.textContent = message;
    statusNode.dataset.variant = variant;
  }

  function toggleRenderButton() {
    const hasRecords = lastParseResult.records.length > 0;
    renderBtn.disabled = livePreview.checked || !hasRecords;
    renderBtn.title = renderBtn.disabled
      ? "Désactivez l'aperçu automatique pour utiliser ce bouton."
      : '';
  }
})();
