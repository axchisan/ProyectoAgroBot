document.addEventListener("DOMContentLoaded", () => {
  // Inicializar animaciones y efectos
  initializeAnimations()
  initializeInteractions()
  initializeFormHandlers()

  // Auto scroll para mensajes de chat
  const chatMessages = document.getElementById("chatMessages")
  if (chatMessages) {
    chatMessages.scrollTop = chatMessages.scrollHeight
  }
})

// Animaciones generales
function initializeAnimations() {
  // Animar elementos al cargar
  const animatedElements = document.querySelectorAll(".recommendation-card, .weather-card, .metric-item, .help-option")
  animatedElements.forEach((element, index) => {
    element.style.opacity = "0"
    element.style.transform = "translateY(20px)"

    setTimeout(() => {
      element.style.transition = "all 0.6s cubic-bezier(0.4, 0, 0.2, 1)"
      element.style.opacity = "1"
      element.style.transform = "translateY(0)"
    }, index * 100)
  })

  // Animar barras de progreso
  const progressBars = document.querySelectorAll(".progress-fill")
  progressBars.forEach((bar, index) => {
    setTimeout(
      () => {
        bar.style.transform = "scaleX(1)"
      },
      index * 200 + 500,
    )
  })

  // Animar gráficos
  const chartBars = document.querySelectorAll(".bar")
  chartBars.forEach((bar, index) => {
    const originalHeight = bar.style.height
    bar.style.height = "0%"

    setTimeout(
      () => {
        bar.style.transition = "height 1s ease-out"
        bar.style.height = originalHeight
      },
      index * 100 + 1000,
    )
  })
}

// Interacciones de botones y elementos
function initializeInteractions() {
  // Efecto de click en botones
  const buttons = document.querySelectorAll(
    "button, .btn-primary-custom, .btn-secondary-modern, .btn-primary-modern, .btn-outline-modern, .action-btn",
  )
  buttons.forEach((button) => {
    button.addEventListener("click", (e) => {
      // Efecto ripple
      createRippleEffect(e, button)

      // Animación de escala
      button.style.transform = "scale(0.95)"
      setTimeout(() => {
        button.style.transform = "scale(1)"
      }, 150)
    })
  })

  // Hover effects para cards
  const cards = document.querySelectorAll(".recommendation-card, .weather-card, .help-option, .contact-card")
  cards.forEach((card) => {
    card.addEventListener("mouseenter", () => {
      card.style.transform = "translateY(-5px)"
    })

    card.addEventListener("mouseleave", () => {
      card.style.transform = "translateY(0)"
    })
  })

  // Parallax effect para elementos flotantes
  if (window.innerWidth > 768) {
    window.addEventListener("mousemove", (e) => {
      const clouds = document.querySelectorAll(".cloud")
      const sun = document.querySelector(".sun")

      const mouseX = e.clientX / window.innerWidth
      const mouseY = e.clientY / window.innerHeight

      clouds.forEach((cloud, index) => {
        const speed = (index + 1) * 0.5
        cloud.style.transform = `translate(${mouseX * speed}px, ${mouseY * speed}px)`
      })

      if (sun) {
        sun.style.transform = `translate(${mouseX * 2}px, ${mouseY * 2}px)`
      }
    })
  }
}

// Manejadores de formularios
function initializeFormHandlers() {
  // Chat form
  const chatForm = document.getElementById("chatForm")
  if (chatForm) {
    chatForm.addEventListener("submit", handleChatSubmit)
  }

  // Input focus effects
  const inputs = document.querySelectorAll("input, textarea")
  inputs.forEach((input) => {
    input.addEventListener("focus", () => {
      input.parentElement.style.transform = "scale(1.02)"
    })

    input.addEventListener("blur", () => {
      input.parentElement.style.transform = "scale(1)"
    })
  })
}

// Manejar envío de chat
function handleChatSubmit(e) {
  const userInput = document.getElementById("userInput")
  const typingIndicator = document.getElementById("typingIndicator")

  if (userInput && userInput.value.trim()) {
    // Mostrar indicador de escritura
    if (typingIndicator) {
      typingIndicator.classList.remove("d-none")
    }

    // Simular delay de respuesta
    setTimeout(
      () => {
        if (typingIndicator) {
          typingIndicator.classList.add("d-none")
        }
      },
      Math.random() * 2000 + 1000,
    )

    // Limpiar input después del envío
    setTimeout(() => {
      userInput.value = ""
    }, 100)
  }
}

// Crear efecto ripple
function createRippleEffect(event, element) {
  const ripple = document.createElement("span")
  const rect = element.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  const x = event.clientX - rect.left - size / 2
  const y = event.clientY - rect.top - size / 2

  ripple.style.width = ripple.style.height = size + "px"
  ripple.style.left = x + "px"
  ripple.style.top = y + "px"
  ripple.classList.add("ripple")

  // Agregar estilos CSS para el ripple
  ripple.style.position = "absolute"
  ripple.style.borderRadius = "50%"
  ripple.style.background = "rgba(255, 255, 255, 0.6)"
  ripple.style.transform = "scale(0)"
  ripple.style.animation = "ripple 0.6s linear"
  ripple.style.pointerEvents = "none"

  element.style.position = "relative"
  element.style.overflow = "hidden"
  element.appendChild(ripple)

  setTimeout(() => {
    ripple.remove()
  }, 600)
}

// Funciones específicas para cada página
function toggleMenu() {
  const overlay = document.getElementById("menuOverlay")
  if (overlay) {
    overlay.classList.toggle("active")
  }
}

function toggleFilters() {
  const filtersSection = document.getElementById("filtersSection")
  if (filtersSection) {
    filtersSection.classList.toggle("active")
  }
}

function toggleFAQ(element) {
  const faqItem = element.parentElement
  const answer = faqItem.querySelector(".faq-answer")
  const icon = element.querySelector("i")

  faqItem.classList.toggle("active")

  if (faqItem.classList.contains("active")) {
    answer.style.maxHeight = answer.scrollHeight + "px"
    icon.style.transform = "rotate(180deg)"
  } else {
    answer.style.maxHeight = "0"
    icon.style.transform = "rotate(0deg)"
  }
}

function refreshWeather() {
  const refreshBtn = document.querySelector(".refresh-btn i")
  if (refreshBtn) {
    refreshBtn.style.animation = "spin 1s linear"
    setTimeout(() => {
      refreshBtn.style.animation = ""
      // Aquí  lógica para actualizar datos
      showNotification("Datos del clima actualizados", "success")
    }, 1000)
  }
}

// Sistema de notificaciones
function showNotification(message, type = "info") {
  const notification = document.createElement("div")
  notification.className = `notification notification-${type}`
  notification.textContent = message

  // Estilos para la notificación
  notification.style.position = "fixed"
  notification.style.top = "20px"
  notification.style.right = "20px"
  notification.style.padding = "15px 20px"
  notification.style.borderRadius = "8px"
  notification.style.color = "white"
  notification.style.fontWeight = "500"
  notification.style.zIndex = "9999"
  notification.style.transform = "translateX(100%)"
  notification.style.transition = "transform 0.3s ease"

  // Colores según el tipo
  switch (type) {
    case "success":
      notification.style.background = "#00b894"
      break
    case "warning":
      notification.style.background = "#fdcb6e"
      break
    case "error":
      notification.style.background = "#e17055"
      break
    default:
      notification.style.background = "#4a7c59"
  }

  document.body.appendChild(notification)

  // Animar entrada
  setTimeout(() => {
    notification.style.transform = "translateX(0)"
  }, 100)

  // Remover después de 3 segundos
  setTimeout(() => {
    notification.style.transform = "translateX(100%)"
    setTimeout(() => {
      notification.remove()
    }, 300)
  }, 3000)
}

// Funciones de utilidad
function formatDate(date) {
  return new Intl.DateTimeFormat("es-ES", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date)
}

function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Lazy loading para imágenes
function initializeLazyLoading() {
  const images = document.querySelectorAll("img[data-src]")
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target
        img.src = img.dataset.src
        img.classList.remove("lazy")
        imageObserver.unobserve(img)
      }
    })
  })

  images.forEach((img) => imageObserver.observe(img))
}

// Inicializar lazy loading si hay imágenes
if (document.querySelectorAll("img[data-src]").length > 0) {
  initializeLazyLoading()
}

// Service Worker para PWA (opcional)
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .then((registration) => {
        console.log("SW registered: ", registration)
      })
      .catch((registrationError) => {
        console.log("SW registration failed: ", registrationError)
      })
  })
}

// Agregar estilos CSS para animaciones
const style = document.createElement("style")
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .notification {
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .lazy {
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .lazy.loaded {
        opacity: 1;
    }
`
document.head.appendChild(style)

// Exportar funciones globales
window.toggleMenu = toggleMenu
window.toggleFilters = toggleFilters
window.toggleFAQ = toggleFAQ
window.refreshWeather = refreshWeather
window.showNotification = showNotification
