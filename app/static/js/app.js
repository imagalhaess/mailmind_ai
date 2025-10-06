// MailMind - Frontend JavaScript
class EmailAnalyzer {
  constructor() {
    this.currentTab = "analyze";
    this.selectedFile = null; // Armazena o arquivo selecionado
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setupFileUpload();
    this.setupTabs();
    this.setupAccessibility();
    this.setupAnimations();
    this.setupEasterEgg();
  }

  setupEventListeners() {
    // Tab navigation
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const tab = item.dataset.tab;
        this.switchTab(tab);
      });
    });

    // Input type radio buttons
    document.querySelectorAll('input[name="inputType"]').forEach((radio) => {
      radio.addEventListener("change", (e) => {
        this.toggleInputType(e.target.value);
      });
    });

    // Analyze button
    const analyzeBtn = document.getElementById("analyzeBtn");
    if (analyzeBtn) {
      analyzeBtn.addEventListener("click", () => {
        this.handleAnalyze();
      });
    }

    // Test buttons
    const testSpamBtn = document.getElementById("testSpamBtn");
    if (testSpamBtn) {
      testSpamBtn.addEventListener("click", () => {
        this.handleTest("improdutivo");
      });
    }

    const testProdutivoBtn = document.getElementById("testProdutivoBtn");
    if (testProdutivoBtn) {
      testProdutivoBtn.addEventListener("click", () => {
        this.handleTest("produtivo");
      });
    }

    // Webhook buttons removidos - funcionalidade desabilitada

    // Test tab buttons - duplicação removida, já configurados acima
  }

  setupFileUpload() {
    const fileUpload = document.getElementById("fileUpload");
    const fileInput = document.getElementById("fileInput");
    const fileInfo = document.getElementById("fileInfo");
    const selectFileBtn = document.getElementById("selectFileBtn");

    // Drag and drop
    fileUpload.addEventListener("dragover", (e) => {
      e.preventDefault();
      fileUpload.classList.add("dragging");
    });

    fileUpload.addEventListener("dragleave", () => {
      fileUpload.classList.remove("dragging");
    });

    fileUpload.addEventListener("drop", (e) => {
      e.preventDefault();
      fileUpload.classList.remove("dragging");

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.handleFileSelect(files[0]);
      }
    });

    // File input change
    fileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        this.handleFileSelect(e.target.files[0]);
      }
    });

    // Click to select file - apenas na área de drop, não no botão
    fileUpload.addEventListener("click", (e) => {
      // Evita conflito com o botão
      if (
        e.target === fileUpload ||
        e.target.classList.contains("file-text") ||
        e.target.classList.contains("file-hint")
      ) {
        fileInput.click();
      }
    });

    // Botão separado para seleção
    selectFileBtn.addEventListener("click", (e) => {
      e.stopPropagation(); // Evita propagação para o fileUpload
      fileInput.click();
    });
  }

  setupTabs() {
    // Initialize with analyze tab active
    this.switchTab("analyze");
  }

  switchTab(tabName) {
    // Update navigation
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.classList.remove("active");
      item.removeAttribute("aria-current");
    });
    const activeNavItem = document.querySelector(`[data-tab="${tabName}"]`);
    activeNavItem.classList.add("active");
    activeNavItem.setAttribute("aria-current", "page");

    // Update tab content
    document.querySelectorAll(".tab-content").forEach((content) => {
      content.classList.remove("active");
      content.setAttribute("aria-hidden", "true");
    });
    const activeTab = document.getElementById(`${tabName}-tab`);
    activeTab.classList.add("active");
    activeTab.setAttribute("aria-hidden", "false");

    this.currentTab = tabName;

    // Anunciar mudança de aba para leitores de tela
    const announcement = document.createElement("div");
    announcement.setAttribute("aria-live", "polite");
    announcement.setAttribute("aria-atomic", "true");
    announcement.className = "sr-only";
    announcement.textContent = `Aba ${tabName} ativada`;
    document.body.appendChild(announcement);

    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }

  toggleInputType(type) {
    const textInput = document.getElementById("text-input");
    const fileInput = document.getElementById("file-input");

    if (type === "text") {
      textInput.style.display = "block";
      fileInput.style.display = "none";
    } else {
      textInput.style.display = "none";
      fileInput.style.display = "block";
    }
  }

  handleFileSelect(file) {
    const allowedTypes = ["text/plain", "application/pdf"];

    if (!allowedTypes.includes(file.type)) {
      this.showToast("Apenas arquivos .txt e .pdf são permitidos", "error");
      return;
    }

    // Armazena o arquivo selecionado para uso posterior
    this.selectedFile = file;

    const fileInfo = document.getElementById("fileInfo");
    fileInfo.innerHTML = `Arquivo selecionado: <strong>${file.name}</strong>`;
    fileInfo.style.display = "block";

    this.showToast(`Arquivo "${file.name}" selecionado`, "success");
  }

  async handleAnalyze() {
    const inputType = document.querySelector(
      'input[name="inputType"]:checked'
    ).value;
    const emailContent = document.getElementById("emailContent").value.trim();
    const senderEmail = document.getElementById("senderEmail").value.trim();

    // Validation
    if (inputType === "text" && !emailContent) {
      this.showToast("Por favor, insira o conteúdo do email", "error");
      return;
    }

    if (inputType === "file" && !this.selectedFile) {
      this.showToast("Por favor, selecione um arquivo", "error");
      return;
    }

    const analyzeBtn = document.getElementById("analyzeBtn");
    const analyzeText = document.getElementById("analyzeText");

    this.setLoading(analyzeBtn, analyzeText, "Analisando...");

    try {
      let result;

      if (inputType === "file") {
        result = await this.uploadFile(this.selectedFile);
      } else {
        result = await this.analyzeText(emailContent, senderEmail);
      }

      this.showResult(result);
      this.showToast("Email analisado com sucesso!", "success");
    } catch (error) {
      console.error("Erro na análise:", error);
      this.showToast(`Erro ao analisar email: ${error.message}`, "error");
    } finally {
      this.setLoading(analyzeBtn, analyzeText, "Analisar Email", false);
    }
  }

  async handleTest(testType) {
    console.log("🧪 Iniciando teste:", testType);

    // Mapear testType para o ID correto do botão
    let buttonId;
    if (testType === "improdutivo") {
      buttonId = "testSpamBtn";
    } else if (testType === "produtivo") {
      buttonId = "testProdutivoBtn";
    } else {
      buttonId = `#test${
        testType.charAt(0).toUpperCase() + testType.slice(1)
      }Btn`;
    }

    console.log("🔍 Procurando botão com ID:", buttonId);
    const testBtn = document.getElementById(buttonId);

    if (!testBtn) {
      console.error("❌ Botão não encontrado:", buttonId);
      this.showToast("Botão de teste não encontrado", "error");
      return;
    }

    console.log("✅ Botão encontrado:", testBtn);
    const testText = testBtn.querySelector("span") || testBtn;

    this.setLoading(testBtn, testText, "Executando...");

    try {
      const result = await this.runTest(testType);
      this.showResult(result);
      this.showToast(`Teste de email ${testType} executado!`, "success");
    } catch (error) {
      console.error("Erro no teste:", error);
      this.showToast("Erro ao executar teste. Tente novamente.", "error");
    } finally {
      this.setLoading(testBtn, testText, "Executar Teste", false);
    }
  }

  loadTestWebhookData() {
    const testData = {
      sender: "teste@exemplo.com",
      subject: "Teste de Webhook",
      content: "Este é um email de teste enviado via webhook.",
    };

    const webhookData = document.getElementById("webhookData");
    webhookData.value = JSON.stringify(testData, null, 2);
    this.showToast("JSON de teste carregado!", "success");
  }

  async handleWebhook() {
    const webhookData = document.getElementById("webhookData").value.trim();
    const webhookBtn = document.getElementById("webhookBtn");
    const webhookText = document.getElementById("webhookText");

    if (!webhookData) {
      this.showToast("Por favor, insira os dados JSON", "error");
      return;
    }

    this.setLoading(webhookBtn, webhookText, "Enviando...");

    try {
      // Debug: mostrar o JSON que está sendo enviado
      console.log("JSON sendo enviado:", webhookData);

      const data = JSON.parse(webhookData);
      console.log("JSON parseado:", data);

      const result = await this.testWebhook(data);
      this.showResult(result);
      this.showToast("Dados enviados para webhook com sucesso!", "success");
    } catch (error) {
      console.error("Erro no webhook:", error);
      console.error("JSON problemático:", webhookData);

      if (error instanceof SyntaxError) {
        this.showToast(`JSON inválido: ${error.message}`, "error");
      } else {
        this.showToast(
          `Erro ao enviar dados para webhook: ${error.message}`,
          "error"
        );
      }
    } finally {
      this.setLoading(webhookBtn, webhookText, "Enviar para Webhook", false);
    }
  }

  async analyzeText(emailContent, senderEmail) {
    try {
      const response = await fetch("/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email_content: emailContent,
          sender: senderEmail || undefined,
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Se retornou job_id, aguarda processamento
      if (result.job_id) {
        return await this.waitForJob(result.job_id);
      }
      
      return result;
    } catch (error) {
      throw error;
    }
  }

  async uploadFile(file) {
    const formData = new FormData();
    formData.append("email_file", file);

    try {
      const response = await fetch("/analyze", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error || `HTTP error! status: ${response.status}`
        );
      }

      const result = await response.json();
      
      // Se retornou job_ids (múltiplos emails), aguarda todos
      if (result.job_ids) {
        return await this.waitForMultipleJobs(result.job_ids);
      }
      
      // Se retornou job_id (email único), aguarda processamento
      if (result.job_id) {
        return await this.waitForJob(result.job_id);
      }
      
      return result;
    } catch (error) {
      throw error;
    }
  }

  async runTest(testType) {
    console.log("🧪 Executando teste:", testType);

    // Mapear testType para o endpoint correto
    let endpoint;
    if (testType === "improdutivo") {
      endpoint = "/test/spam"; // Mapear improdutivo para spam
    } else if (testType === "produtivo") {
      endpoint = "/test/produtivo";
    } else {
      endpoint = `/test/${testType}`;
    }

    console.log("🔗 Endpoint:", endpoint);

    const response = await fetch(endpoint, {
      method: "GET",
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("❌ Erro na resposta:", errorText);
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async testWebhook(data) {
    const response = await fetch("/webhook/email", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error || `HTTP error! status: ${response.status}`
      );
    }

    const result = await response.json();
    
    // Se retornou job_id, aguarda processamento
    if (result.job_id) {
      return await this.waitForJob(result.job_id);
    }
    
    return result;
  }

  async waitForJob(jobId) {
    const maxAttempts = 60; // 60 tentativas = 1 minuto
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      try {
        const response = await fetch(`/analyze/status/${jobId}`);
        const status = await response.json();
        
        if (status.status === "completed") {
          return status.result;
        } else if (status.status === "error") {
          throw new Error(status.error || "Erro no processamento");
        }
        
        // Aguarda 1 segundo antes da próxima tentativa
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
        
      } catch (error) {
        if (attempts >= maxAttempts - 1) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
      }
    }
    
    throw new Error("Timeout: Análise demorou mais que o esperado");
  }

  async waitForMultipleJobs(jobIds) {
    const results = [];
    
    for (const jobId of jobIds) {
      try {
        const result = await this.waitForJob(jobId);
        results.push(result);
      } catch (error) {
        results.push({
          categoria: "❌ ERRO",
          atencao_humana: "SIM",
          resumo: `Falha na análise: ${error.message}`,
          sugestao: "Verifique o conteúdo e tente novamente",
          sender: "Não identificado",
          acao: "⚠️ Erro no processamento",
          cached: false
        });
      }
    }
    
    return {
      total_emails: jobIds.length,
      results: results,
      message: `✅ Análise concluída para ${jobIds.length} email(s)`
    };
  }

  showResult(result) {
    const resultsSection = document.getElementById("results");
    const resultContent = document.getElementById("resultContent");

    console.log("Resultado recebido:", result); // Debug

    // Handle webhook result (tem estrutura diferente)
    if (result.result && result.result.categoria) {
      resultContent.innerHTML = this.formatSingleResult(result.result);
    }
    // Handle single result (API retorna 'categoria' e 'atencao_humana')
    else if (result.categoria || result.atencao_humana) {
      resultContent.innerHTML = this.formatSingleResult(result);
    }
    // Handle batch results with 'results' array
    else if (result.results && Array.isArray(result.results)) {
      resultContent.innerHTML = this.formatBatchResultsWithResults(result);
    }
    // Handle batch results with 'resultados' array
    else if (
      result.tipo === "lote" &&
      result.resultados &&
      Array.isArray(result.resultados)
    ) {
      resultContent.innerHTML = this.formatBatchResults(result);
    }
    // Handle error
    else if (result.error) {
      resultContent.innerHTML = `
                <div class="result-item">
                    <div class="result-status destructive">Erro</div>
                    <div class="result-summary">${result.error}</div>
                </div>
            `;
    }
    // Handle other cases
    else {
      resultContent.innerHTML = `
                <div class="result-item">
                    <div class="result-status">Resultado</div>
                    <div class="result-summary">${JSON.stringify(
                      result,
                      null,
                      2
                    )}</div>
                </div>
            `;
    }

    resultsSection.style.display = "block";
    resultsSection.scrollIntoView({ behavior: "smooth" });
  }

  formatSingleResult(result) {
    // Determina se é produtivo ou improdutivo baseado na categoria
    const categoria = result.categoria ? result.categoria.toLowerCase() : "";
    
    // Categorias improdutivas: spam, erro, outro (quando não identificado)
    const isImprodutivo = categoria === "spam" || categoria === "erro";
    
    // Categorias produtivas: produtivo, consulta, reclamação, urgente, etc.
    const isProdutivo = !isImprodutivo && categoria !== "" && categoria !== "n/a";
    
    let statusClass, statusText;
    if (isImprodutivo) {
      statusClass = "improdutivo";
      statusText = "Improdutivo";
    } else if (isProdutivo) {
      statusClass = "produtivo";
      statusText = "Produtivo";
    } else {
      statusClass = "";
      statusText = "Indefinido";
    }

    return `
            <div class="result-item">
                <div class="result-status ${statusClass}">${statusText}</div>
                <div class="result-summary">
                    <strong>Categoria:</strong> ${result.categoria || "N/A"}
                </div>
                <div class="result-summary">
                    <strong>Resumo:</strong> ${result.resumo || "N/A"}
                </div>
                <div class="result-actions">
                    <strong>Sugestão:</strong> ${
                      result.sugestao ||
                      result.sugestao_resposta_ou_acao ||
                      "N/A"
                    }
                </div>
                <div class="result-actions">
                    <strong>Ação:</strong> ${result.acao || "N/A"}
                </div>
            </div>
        `;
  }

  formatBatchResultsWithResults(result) {
    // Conta emails produtivos e improdutivos baseado na categoria
    const improdutivos = result.results.filter(
      (r) => {
        const cat = r.categoria ? r.categoria.toLowerCase() : "";
        return cat === "spam" || cat === "erro";
      }
    ).length;
    
    const produtivos = result.results.filter(
      (r) => {
        const cat = r.categoria ? r.categoria.toLowerCase() : "";
        return cat !== "spam" && cat !== "erro" && cat !== "" && cat !== "n/a";
      }
    ).length;

    let html = `
            <div class="result-item">
                <div class="result-summary">
                    <strong>Total de emails processados:</strong> ${result.results.length}
                </div>
                <div class="result-actions">
                    <strong>Emails produtivos:</strong> ${produtivos}
                </div>
                <div class="result-actions">
                    <strong>Emails improdutivos:</strong> ${improdutivos}
                </div>
            </div>
        `;

    result.results.forEach((emailResult, index) => {
      html += this.formatSingleResult(emailResult);
    });

    return html;
  }

  formatBatchResults(result) {
    // Conta emails produtivos e improdutivos baseado na categoria
    const improdutivos = result.resultados.filter(
      (r) => {
        const cat = r.categoria ? r.categoria.toLowerCase() : "";
        return cat === "spam" || cat === "erro";
      }
    ).length;
    
    const produtivos = result.resultados.filter(
      (r) => {
        const cat = r.categoria ? r.categoria.toLowerCase() : "";
        return cat !== "spam" && cat !== "erro" && cat !== "" && cat !== "n/a";
      }
    ).length;

    let html = `
            <div class="result-item">
                <div class="result-summary">
                    <strong>Total de emails processados:</strong> ${
                      result.total_emails || result.resultados.length
                    }
                </div>
                <div class="result-actions">
                    <strong>Emails produtivos:</strong> ${produtivos}
                </div>
                <div class="result-actions">
                    <strong>Emails improdutivos:</strong> ${improdutivos}
                </div>
            </div>
        `;

    result.resultados.forEach((emailResult, index) => {
      html += this.formatSingleResult(emailResult);
    });

    return html;
  }

  setLoading(button, textElement, loadingText, isLoading = true) {
    if (isLoading) {
      button.disabled = true;
      textElement.innerHTML = `
                <div class="spinner"></div>
                ${loadingText}
            `;
    } else {
      button.disabled = false;
      textElement.innerHTML = loadingText;
    }
  }

  showToast(message, type = "success") {
    const toastContainer = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toast.setAttribute("role", "alert");
    toast.setAttribute("aria-live", "polite");

    toastContainer.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
      toast.remove();
    }, 5000);
  }

  setupAccessibility() {
    // Melhorar navegação por teclado
    document.addEventListener("keydown", (e) => {
      // ESC para fechar modais ou voltar
      if (e.key === "Escape") {
        const activeModal = document.querySelector(".modal.active");
        if (activeModal) {
          this.closeModal(activeModal);
        }
      }

      // Enter e Space para botões
      if (
        (e.key === "Enter" || e.key === " ") &&
        e.target.classList.contains("btn")
      ) {
        e.preventDefault();
        e.target.click();
      }
    });

    // Adicionar ARIA labels dinâmicos
    this.updateAriaLabels();
  }

  setupAnimations() {
    // Adicionar animações suaves aos elementos
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("animate-slide-up");
        }
      });
    });

    // Observar elementos que devem ser animados
    document.querySelectorAll(".card, .test-card").forEach((el) => {
      observer.observe(el);
    });
  }

  updateAriaLabels() {
    // Atualizar labels ARIA dinamicamente
    const analyzeBtn = document.getElementById("analyzeBtn");
    if (analyzeBtn) {
      analyzeBtn.setAttribute(
        "aria-label",
        "Analisar email com inteligência artificial"
      );
    }

    const fileInput = document.getElementById("fileInput");
    if (fileInput) {
      fileInput.setAttribute(
        "aria-label",
        "Selecionar arquivo de email para análise"
      );
    }

    const emailContent = document.getElementById("emailContent");
    if (emailContent) {
      emailContent.setAttribute(
        "aria-label",
        "Digite ou cole o conteúdo do email para análise"
      );
    }
  }

  closeModal(modal) {
    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");
  }

  setupEasterEgg() {
    const easterEggBtn = document.getElementById("easterEggBtn");
    const easterEggPopup = document.getElementById("easterEggPopup");
    const easterEggImage = document.getElementById("easterEggImage");

    if (
      !this.validateEasterEggElements(
        easterEggBtn,
        easterEggPopup,
        easterEggImage
      )
    ) {
      return;
    }

    this.initializeEasterEggEvents(
      easterEggBtn,
      easterEggPopup,
      easterEggImage
    );
  }

  validateEasterEggElements(btn, popup, image) {
    return btn && popup && image;
  }

  initializeEasterEggEvents(btn, popup, image) {
    btn.addEventListener("click", () => this.showEasterEgg(popup, image));
    btn.addEventListener("keydown", (e) =>
      this.handleEasterEggKeydown(e, popup, image)
    );
  }

  handleEasterEggKeydown(event, popup, image) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      this.showEasterEgg(popup, image);
    }
  }

  showEasterEgg(popup, imageElement) {
    const randomImagePath = this.getRandomImagePath();

    this.loadImageWithFallback(imageElement, randomImagePath);
    this.displayPopup(popup);
    this.schedulePopupClose(popup);
  }

  getRandomImagePath() {
    // Lista de TODAS as imagens JPG da pasta (excluindo Zone.Identifier)
    const availableImages = [
      "/static/images/IMG-20251003-WA0014.jpg",
      "/static/images/IMG-20251003-WA0015.jpg",
      "/static/images/IMG-20251003-WA0016.jpg",
      "/static/images/IMG-20251003-WA0017.jpg",
      "/static/images/IMG-20251003-WA0018.jpg",
      "/static/images/IMG-20251003-WA0019.jpg",
      "/static/images/IMG-20251003-WA0020.jpg",
      "/static/images/IMG-20251003-WA0021.jpg",
      "/static/images/IMG-20251003-WA0022.jpg",
      "/static/images/IMG-20251003-WA0023.jpg",
      "/static/images/IMG-20251003-WA0024.jpg",
      "/static/images/IMG-20251003-WA0025.jpg",
      "/static/images/IMG-20251003-WA0026.jpg",
      "/static/images/IMG-20251003-WA0027.jpg",
      "/static/images/IMG-20251003-WA0028.jpg",
      "/static/images/IMG-20251003-WA0029.jpg",
      "/static/images/IMG-20251003-WA0030.jpg",
      "/static/images/IMG-20251003-WA0031.jpg",
      "/static/images/IMG-20251003-WA0032.jpg",
      "/static/images/IMG-20251003-WA0033.jpg",
      "/static/images/IMG-20251003-WA0034.jpg",
      "/static/images/IMG-20251003-WA0035.jpg",
      "/static/images/IMG-20251003-WA0036.jpg",
      "/static/images/IMG-20251003-WA0037.jpg",
      "/static/images/IMG-20251003-WA0038.jpg",
    ];

    const randomIndex = Math.floor(Math.random() * availableImages.length);
    return availableImages[randomIndex];
  }

  loadImageWithFallback(imageElement, imagePath) {
    // Debug: log para verificar qual imagem está sendo carregada
    console.log("Tentando carregar:", imagePath);

    imageElement.src = imagePath;

    imageElement.onerror = () => {
      console.log("Erro ao carregar imagem:", imagePath);
      // Fallback para uma imagem padrão ou placeholder
      imageElement.src =
        "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzZjNzI4MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlbSBuw6NvIGVuY29udHJhZGE8L3RleHQ+PC9zdmc+";
    };

    imageElement.onload = () => {
      console.log("Imagem carregada com sucesso:", imagePath);
    };
  }

  displayPopup(popup) {
    popup.classList.add("active");
    popup.setAttribute("aria-hidden", "false");
  }

  schedulePopupClose(popup) {
    setTimeout(() => {
      popup.classList.remove("active");
      popup.setAttribute("aria-hidden", "true");
    }, 2000); // 2 segundos
  }
}

// Initialize the application when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new EmailAnalyzer();
});
