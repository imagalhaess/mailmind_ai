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
    } else {
      console.error("Botão analyzeBtn não encontrado!");
    }

    // Test buttons - verificação segura
    const testSpamBtn = document.getElementById("testSpamBtn");
    const testProductiveBtn = document.getElementById("testProductiveBtn");
    
    console.log("Test buttons found:", { testSpamBtn, testProductiveBtn });
    
    if (testSpamBtn) {
      testSpamBtn.addEventListener("click", () => {
        console.log("Botão spam clicado!");
        this.handleTest("spam");
      });
    } else {
      console.error("Botão testSpamBtn não encontrado!");
    }

    if (testProductiveBtn) {
      testProductiveBtn.addEventListener("click", () => {
        console.log("Botão produtivo clicado!");
        this.handleTest("produtivo");
      });
    } else {
      console.error("Botão testProductiveBtn não encontrado!");
    }

    // Webhook button
    const webhookBtn = document.getElementById("webhookBtn");
    if (webhookBtn) {
      webhookBtn.addEventListener("click", () => {
        this.handleWebhook();
      });
    } else {
      console.error("Botão webhookBtn não encontrado!");
    }

    // Webhook test button
    const webhookTestBtn = document.getElementById("webhookTestBtn");
    if (webhookTestBtn) {
      webhookTestBtn.addEventListener("click", () => {
        this.loadTestWebhookData();
      });
    } else {
      console.error("Botão webhookTestBtn não encontrado!");
    }

    // Test tab buttons - verificação segura
    const testImprodutivoBtn = document.getElementById("testImprodutivoBtn");
    const testProdutivoBtn = document.getElementById("testProdutivoBtn");
    
    console.log("Test tab buttons found:", { testImprodutivoBtn, testProdutivoBtn });
    
    if (testImprodutivoBtn) {
      testImprodutivoBtn.addEventListener("click", () => {
        console.log("Botão improdutivo clicado!");
        this.handleTest("spam");
      });
    } else {
      console.error("Botão testImprodutivoBtn não encontrado!");
    }

    if (testProdutivoBtn) {
      testProdutivoBtn.addEventListener("click", () => {
        console.log("Botão produtivo clicado!");
        this.handleTest("produtivo");
      });
    } else {
      console.error("Botão testProdutivoBtn não encontrado!");
    }
  }

  setupFileUpload() {
    // Aguarda um pouco para garantir que o DOM esteja totalmente carregado
    setTimeout(() => {
      const fileUpload = document.getElementById("fileUpload");
      const fileInput = document.getElementById("fileInput");
      const fileInfo = document.getElementById("fileInfo");
      const selectFileBtn = document.getElementById("selectFileBtn");

      // Debug: verificar se elementos existem
      console.log("File upload elements:", { fileUpload, fileInput, fileInfo, selectFileBtn });
      
      if (!fileUpload || !fileInput || !selectFileBtn) {
        console.error("Elementos de upload não encontrados!");
        return;
      }

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
        console.log("Arquivo selecionado:", e.target.files);
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
          console.log("Área de upload clicada, abrindo seletor...");
          fileInput.click();
        }
      });

      // Botão separado para seleção - versão mais robusta
      selectFileBtn.addEventListener("click", (e) => {
        console.log("Botão selecionar arquivo clicado!");
        e.preventDefault();
        e.stopPropagation();
        
        // Força o clique no input de arquivo
        try {
          fileInput.click();
          console.log("Seletor de arquivo aberto com sucesso!");
        } catch (error) {
          console.error("Erro ao abrir seletor de arquivo:", error);
        }
      });

      console.log("File upload setup concluído!");
    }, 100);
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
    console.log(`Iniciando teste: ${testType}`);
    
    const testBtn = document.querySelector(
      `#test${testType.charAt(0).toUpperCase() + testType.slice(1)}Btn`
    );
    
    if (!testBtn) {
      console.error(`Botão de teste não encontrado para: ${testType}`);
      this.showToast("Erro: Botão de teste não encontrado", "error");
      return;
    }
    
    const testText = testBtn.querySelector("span") || testBtn;

    this.setLoading(testBtn, testText, "Executando...");

    try {
      console.log(`Fazendo requisição para /test/${testType}`);
      const result = await this.runTest(testType);
      console.log("Resultado do teste:", result);
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
    const response = await fetch("/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email_content: emailContent,
        sender: senderEmail || undefined,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async uploadFile(file) {
    const formData = new FormData();
    formData.append("email_file", file); // Corrigido: usar 'email_file' como esperado pelo backend

    const response = await fetch("/analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error || `HTTP error! status: ${response.status}`
      );
    }

    return await response.json();
  }

  async runTest(testType) {
    const response = await fetch(`/test/${testType}`, {
      method: "GET",
    });

    if (!response.ok) {
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

    return await response.json();
  }

  showResult(result) {
    const resultsSection = document.getElementById("results");
    const resultContent = document.getElementById("resultContent");

    // Handle webhook result (tem estrutura diferente)
    if (result.result && result.result.categoria) {
      resultContent.innerHTML = this.formatSingleResult(result.result);
    }
    // Handle single result (API retorna 'categoria' e 'atencao_humana')
    else if (result.categoria || result.atencao_humana) {
      resultContent.innerHTML = this.formatSingleResult(result);
    }
    // Handle batch results
    else if (result.results && Array.isArray(result.results)) {
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
    // Determina se é produtivo baseado na atenção humana
    const isProdutivo = result.atencao_humana === "SIM";
    const statusClass = isProdutivo ? "produtivo" : "improdutivo";
    const statusText = isProdutivo ? "Produtivo" : "Improdutivo";

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
                    <strong>Sugestão:</strong> ${result.sugestao || "N/A"}
                </div>
                <div class="result-actions">
                    <strong>Ação Executada:</strong> ${
                      result.acao_executada || "N/A"
                    }
                </div>
            </div>
        `;
  }

  formatBatchResults(result) {
    // Conta emails produtivos (SIM) e improdutivos (NÃO)
    const produtivos = result.results.filter(
      (r) => r.atencao_humana === "SIM"
    ).length;
    const improdutivos = result.results.filter(
      (r) => r.atencao_humana === "NÃO"
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
  console.log("DOM carregado, inicializando EmailAnalyzer...");
  // Pequeno delay para garantir que todos os elementos estejam carregados
  setTimeout(() => {
    new EmailAnalyzer();
  }, 100);
});
