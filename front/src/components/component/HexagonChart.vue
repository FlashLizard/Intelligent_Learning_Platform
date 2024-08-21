<template>
  <div class="hexagon-chart">
    <svg viewBox="-1.2 -1.2 2.4 2.4" width="400" height="400">
      <defs>
        <template v-for="(colorSet, index) in colors" :key="'gradient' + index">
          <linearGradient :id="'gradient' + (index + 1)" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" :style="{ stopColor: colorSet[0], stopOpacity: 1 }" />
            <stop offset="100%" :style="{ stopColor: colorSet[1], stopOpacity: 1 }" />
          </linearGradient>
        </template>
      </defs>

      <polygon :points="points" class="hexagon" />
      <polygon :points="dataPoints" class="data" />
      <line v-for="(line, index) in hexagonLines" :key="index" :x1="line.x1" :y1="line.y1" :x2="line.x2" :y2="line.y2" class="hexagon-line" />
      <template v-for="(point, index) in labelPoints" :key="'label' + index">
        <text v-if="isVerticalLabel(index)" :x="point.x" :y="point.y" :fill="'url(#gradient' + (index + 1) + ')'" class="hexagon-label vertical-label">
          <tspan v-for="(char, charIndex) in labels[index].split('')" :key="charIndex" x="x" dy="1em">{{ char }}</tspan>
        </text>
        <text v-else :x="point.x" :y="point.y" :fill="'url(#gradient' + (index + 1) + ')'" class="hexagon-label">
          {{ labels[index] }}
        </text>
      </template>
    </svg>
  </div>
</template>

<script>
export default {
  props: {
    data: {
      type: Array,
      required: true,
    },
    labels: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      colors: [
        ['#FF5733', '#FF5733'],
        ['#e23c09', '#e23c09'],
        ['#C70039', '#900C3F'],
        ['#581845', '#900C3F'],
        ['#1F618D', '#2874A6'],
        ['#1ABC9C', '#16A085'],
      ],
    };
  },
  computed: {
    points() {
      return this.generateHexagonPoints(1).join(' ');
    },
    dataPoints() {
      return this.generateHexagonPoints(0.95, this.data).join(' ');
    },
    hexagonLines() {
      return this.generateHexagonLines(1);
    },
    labelPoints() {
      return this.generateHexagonPoints(1.1).map((point) => {
        const [x, y] = point.split(',').map(Number);
        return { x, y: y + 0.04 };
      });
    },
  },
  methods: {
    generateHexagonPoints(radius, data = [100, 100, 100, 100, 100, 100]) {
      const angle = Math.PI / 3;
      return data.map((value, index) => {
        const r = radius * value / 100;
        const x = r * Math.cos(angle * index);
        const y = r * Math.sin(angle * index);
        return { x, y };
      }).map(point => `${point.x},${point.y}`);
    },
    generateHexagonLines(radius) {
      const points = this.generateHexagonPoints(radius).map(point => {
        const [x, y] = point.split(',').map(Number);
        return { x, y };
      });
      const lines = [];
      const len = points.length;
      for (let i = 0; i < len; i++) {
        const oppositeIndex = (i + len / 2) % len;
        lines.push({ x1: points[i].x, y1: points[i].y, x2: points[oppositeIndex].x, y2: points[oppositeIndex].y });
      }
      return lines;
    },
    isVerticalLabel(index) {
      return index === 0 || index === 3;
    },
  },
};
</script>

<style scoped>
.hexagon {
  fill: none;
  stroke: rgb(43, 1, 114);
  stroke-width: 0.03;
}
.data {
  fill: rgba(0, 150, 255, 0.3);
  stroke: rgba(0, 150, 255, 0.7);
  stroke-width: 0.03;
}
.hexagon-line {
  stroke: rgb(59, 0, 118);
  stroke-width: 0.01;
}
.hexagon-label {
  font-size: 0.007em;
  font-weight: bold;
  text-anchor: middle;
}

.vertical-label {
  writing-mode: vertical-rl;
  glyph-orientation-vertical: 0;
  text-anchor: middle;
  letter-spacing: 0px !important; 
  font-size: 0.006em;
}
</style>
