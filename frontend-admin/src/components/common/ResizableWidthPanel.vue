<template>
  <div
    ref="rootRef"
    class="resizable-width-panel"
    :class="{ 'is-dragging': isDragging, 'is-disabled': disabled || isStacked, 'handle-visible': isHandleVisible || isDragging }"
    :style="panelStyle"
    @pointermove="updateHandleVisibility"
    @pointerleave="hideHandle"
  >
    <slot />
    <button
      v-if="!disabled && !isStacked"
      type="button"
      class="resize-handle"
      aria-label="拖拽调整卡片宽度"
      @pointerdown="startResize"
    >
      <span></span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';

const props = withDefaults(
  defineProps<{
    panelId: string;
    storageKey?: string;
    defaultWidth?: number;
    minWidth?: number;
    maxWidth?: number;
    disabled?: boolean;
    stackAt?: number;
  }>(),
  {
    storageKey: 'resizable-width-panel',
    defaultWidth: undefined,
    minWidth: 280,
    maxWidth: 1600,
    disabled: false,
    stackAt: 1200,
  },
);

const rootRef = ref<HTMLElement | null>(null);
const width = ref<number | null>(null);
const isDragging = ref(false);
const isHandleVisible = ref(false);
const viewportWidth = ref(typeof window === 'undefined' ? 1440 : window.innerWidth);

let dragStartX = 0;
let dragStartWidth = 0;
const handleRevealDistance = 28;

const isStacked = computed(() => viewportWidth.value <= props.stackAt);

const maxAllowedWidth = computed(() => {
  const viewportLimit = Math.max(props.minWidth, viewportWidth.value - 64);
  return Math.max(props.minWidth, Math.min(props.maxWidth, viewportLimit));
});

const panelStyle = computed(() => {
  if (isStacked.value) {
    return {
      width: '100%',
      minWidth: '0',
      maxWidth: '100%',
    };
  }

  const currentWidth = clampWidth(width.value ?? props.defaultWidth ?? props.minWidth);
  return {
    width: `${currentWidth}px`,
    minWidth: `${props.minWidth}px`,
    maxWidth: `${maxAllowedWidth.value}px`,
  };
});

function storageId() {
  return `${props.storageKey}:${props.panelId}`;
}

function clampWidth(value: number) {
  return Math.min(maxAllowedWidth.value, Math.max(props.minWidth, Math.round(value)));
}

function loadWidth() {
  try {
    const raw = window.localStorage.getItem(storageId());
    if (!raw) return null;
    const parsed = Number(raw);
    return Number.isFinite(parsed) ? clampWidth(parsed) : null;
  } catch {
    return null;
  }
}

function saveWidth(value: number) {
  try {
    window.localStorage.setItem(storageId(), String(clampWidth(value)));
  } catch {
    // Ignore storage failures and keep the UI interactive.
  }
}

function syncViewportWidth() {
  viewportWidth.value = window.innerWidth;
  if (width.value !== null) {
    width.value = clampWidth(width.value);
  }
}

function stopResize() {
  window.removeEventListener('pointermove', resizePanel);
  window.removeEventListener('pointerup', finishResize);
  window.removeEventListener('pointercancel', finishResize);
  document.body.style.userSelect = '';
  document.body.style.cursor = '';
}

function resizePanel(event: PointerEvent) {
  if (!isDragging.value) return;
  width.value = clampWidth(dragStartWidth + event.clientX - dragStartX);
}

function finishResize() {
  if (isDragging.value && width.value !== null) {
    saveWidth(width.value);
  }
  isDragging.value = false;
  isHandleVisible.value = false;
  stopResize();
}

function updateHandleVisibility(event: PointerEvent) {
  if (props.disabled || isStacked.value) return;
  const rect = rootRef.value?.getBoundingClientRect();
  if (!rect) return;
  const distanceToRight = rect.right - event.clientX;
  const inVerticalRange = event.clientY >= rect.top && event.clientY <= rect.bottom;
  isHandleVisible.value = inVerticalRange && distanceToRight >= -4 && distanceToRight <= handleRevealDistance;
}

function hideHandle() {
  if (!isDragging.value) {
    isHandleVisible.value = false;
  }
}

function startResize(event: PointerEvent) {
  if (props.disabled || isStacked.value) return;
  event.preventDefault();
  dragStartX = event.clientX;
  dragStartWidth = width.value ?? rootRef.value?.getBoundingClientRect().width ?? props.defaultWidth ?? props.minWidth;
  isDragging.value = true;
  isHandleVisible.value = true;
  document.body.style.userSelect = 'none';
  document.body.style.cursor = 'ew-resize';
  window.addEventListener('pointermove', resizePanel);
  window.addEventListener('pointerup', finishResize);
  window.addEventListener('pointercancel', finishResize);
}

onMounted(async () => {
  await nextTick();
  viewportWidth.value = window.innerWidth;
  width.value =
    loadWidth() ??
    clampWidth(props.defaultWidth ?? rootRef.value?.getBoundingClientRect().width ?? props.minWidth);
  window.addEventListener('resize', syncViewportWidth);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', syncViewportWidth);
  stopResize();
});
</script>

<style scoped>
.resizable-width-panel {
  position: relative;
  box-sizing: border-box;
  max-width: 100%;
  min-width: 0;
  flex: 0 0 auto;
}

.resizable-width-panel.is-dragging {
  z-index: 5;
}

.resize-handle {
  position: absolute;
  top: 10px;
  right: 6px;
  bottom: 10px;
  width: 14px;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: ew-resize;
  touch-action: none;
  z-index: 6;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition: opacity 0.18s ease, visibility 0.18s ease;
}

.resize-handle span {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 4px;
  transform: translateX(-50%);
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.12);
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.resizable-width-panel.handle-visible .resize-handle,
.resizable-width-panel.is-dragging .resize-handle {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}

.resizable-width-panel.handle-visible .resize-handle span,
.resizable-width-panel.is-dragging .resize-handle span {
  background: rgba(37, 99, 235, 0.28);
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.08);
}

.is-disabled .resize-handle {
  display: none;
}
</style>
