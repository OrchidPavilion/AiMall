<template>
  <div class="page" :class="{ 'paper-shot-mode': paperShotMode }">
    <ResizableWidthPanel
      class="section-card-shell"
      panel-id="analytics-overview-card"
      :storage-key="analyticsWidthStorageKey"
      :default-width="analyticsWidthPresets.overviewCard"
      :min-width="980"
      :max-width="1800"
      :disabled="paperShotMode"
    >
      <el-card v-loading="overviewLoading">
        <template #header>
          <div class="head">
            <span>数据分析与实验结果</span>
            <el-space>
              <el-switch
                v-model="paperShotMode"
                inline-prompt
                active-text="截图模式"
                inactive-text="普通模式"
                class="paper-switch"
              />
              <template v-if="!paperShotMode">
                <el-button @click="loadAll">刷新数据</el-button>
                <el-button type="danger" plain @click="resetBehaviors">清空行为轨迹</el-button>
                <el-button @click="generateBehaviorReplay" :loading="replaying">生成论文实验样本</el-button>
                <el-button type="primary" @click="runExperiment" :loading="running">运行三算法实验</el-button>
              </template>
            </el-space>
          </div>
        </template>
        <div class="scope-tip">当前数据分析与实验统计口径：当前库中的有效行为数据。如果通过“生成论文实验样本”创建样本，这些样本会被直接纳入实验统计。</div>
        <div class="scope-tip">说明：论文实验样本是系统按真实商城访问链路自动生成的可重复数据集，适合在真实访问不足时做论文对比实验。</div>

        <div class="resizable-flow metrics-flow" v-if="overview.data_summary">
          <ResizableWidthPanel
            v-for="m in overviewCards"
            :key="m.label"
            class="metric-card-shell"
            :panel-id="`overview-metric-${m.label}`"
            :storage-key="analyticsWidthStorageKey"
            :default-width="analyticsWidthPresets.metricCard"
            :min-width="180"
            :max-width="420"
            :disabled="paperShotMode"
          >
            <div class="metric-card">
              <div class="metric-label metric-label-row">
                <span>{{ m.label }}</span>
                <el-popover v-if="m.help && !paperShotMode" placement="top" trigger="click" width="320">
                  <template #reference>
                    <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
                  </template>
                  <div class="tip-pop-content">{{ m.help }}</div>
                </el-popover>
              </div>
              <div class="metric-value">{{ m.value }}</div>
            </div>
          </ResizableWidthPanel>
        </div>

        <div class="resizable-flow summary-flow">
          <ResizableWidthPanel
            class="panel-shell"
            panel-id="behavior-distribution-panel"
            :storage-key="analyticsWidthStorageKey"
            :default-width="analyticsWidthPresets.summaryPanel"
            :min-width="320"
            :max-width="860"
            :disabled="paperShotMode"
          >
            <div class="panel">
              <div class="panel-title panel-title-row">
                <span>行为类型分布</span>
                <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="320">
                  <template #reference>
                    <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
                  </template>
                  <div class="tip-pop-content">这是当前真实行为数据里，不同行为类型各出现了多少次。用来判断用户主要是在搜索、浏览，还是已经开始加购和购买。</div>
                </el-popover>
              </div>
              <el-table :data="behaviorRows" size="small" border>
                <el-table-column prop="type" width="180">
                  <template #header>
                    <div class="table-head-with-tip">
                      <span>行为类型</span>
                      <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="280">
                        <template #reference><el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button></template>
                        <div class="tip-pop-content">用户在商城里做了什么事，比如搜索、浏览商品、加入购物车、购买。</div>
                      </el-popover>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="count" width="100">
                  <template #header>
                    <div class="table-head-with-tip">
                      <span>数量</span>
                      <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="260">
                        <template #reference><el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button></template>
                        <div class="tip-pop-content">该行为类型在当前真实数据中出现的次数。</div>
                      </el-popover>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </ResizableWidthPanel>

          <ResizableWidthPanel
            class="panel-shell"
            panel-id="top-customers-panel"
            :storage-key="analyticsWidthStorageKey"
            :default-width="analyticsWidthPresets.summaryPanel"
            :min-width="320"
            :max-width="860"
            :disabled="paperShotMode"
          >
            <div class="panel">
              <div class="panel-title panel-title-row">
                <span>活跃客户 Top10</span>
                <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="320">
                  <template #reference>
                    <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
                  </template>
                  <div class="tip-pop-content">按行为次数从高到低排序的前10名客户。这里的“活跃”指操作次数多，不代表一定下单更多。</div>
                </el-popover>
              </div>
              <el-table :data="overview.top_customers || []" size="small" border>
                <el-table-column prop="customer_name" label="客户" />
                <el-table-column prop="count" width="100">
                  <template #header>
                    <div class="table-head-with-tip">
                      <span>行为数</span>
                      <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="260">
                        <template #reference><el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button></template>
                        <div class="tip-pop-content">该客户在真实行为轨迹里产生的总操作次数。</div>
                      </el-popover>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </ResizableWidthPanel>
        </div>
      </el-card>
    </ResizableWidthPanel>

    <ResizableWidthPanel
      class="section-card-shell"
      panel-id="experiment-records-card"
      :storage-key="analyticsWidthStorageKey"
      :default-width="analyticsWidthPresets.experimentsCard"
      :min-width="720"
      :max-width="1800"
      :disabled="paperShotMode"
    >
      <el-card>
        <template #header>
          <div class="head">
            <div class="panel-title-row">
              <span>实验记录</span>
              <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="340">
                <template #reference>
                  <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
                </template>
                <div class="tip-pop-content">每一条实验记录都是在某一时刻，对“当时数据库中的真实行为快照”运行三种算法后保存的结果。后续行为变化不会改写旧记录。</div>
              </el-popover>
            </div>
            <el-space>
              <span class="head-tip">三算法在同一真实行为快照上对比</span>
              <el-button v-if="!paperShotMode" size="small" type="danger" plain @click="clearExperiments">清空实验记录</el-button>
            </el-space>
          </div>
        </template>
        <el-table :data="experiments" border size="small" @row-click="openExperiment">
          <el-table-column prop="name" label="实验名称" min-width="160" />
          <el-table-column prop="status" label="状态" width="90" />
          <el-table-column prop="message" label="结果说明" min-width="220" />
          <el-table-column prop="created_at" label="时间" min-width="220">
            <template #default="{ row }">
              {{ formatCnTime(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </ResizableWidthPanel>

    <ResizableWidthPanel
      v-if="activeExperiment"
      class="section-card-shell"
      panel-id="active-experiment-card"
      :storage-key="analyticsWidthStorageKey"
      :default-width="analyticsWidthPresets.activeExperimentCard"
      :min-width="920"
      :max-width="1800"
      :disabled="paperShotMode"
    >
      <el-card>
        <template #header>
          <div class="head">
            <span>实验详情：#{{ activeExperiment.id }}</span>
            <el-space>
              <el-button v-if="!paperShotMode" size="small" @click="exportArtifacts" :loading="exporting">导出CSV/PNG/分析稿</el-button>
              <el-button v-if="!paperShotMode" size="small" @click="activeExperiment = null">收起</el-button>
            </el-space>
          </div>
        </template>

        <div v-if="!metricCharts.length" class="empty-state">该实验暂无图表数据（通常是行为数据不足）。</div>
        <div v-else class="resizable-flow chart-flow compact">
          <ResizableWidthPanel
            v-for="chart in metricCharts"
            :key="chart.metric"
            class="chart-card-shell"
            :panel-id="`metric-chart-${chart.metric}-${chart.k}`"
            :storage-key="analyticsWidthStorageKey"
            :default-width="analyticsWidthPresets.chartCard"
            :min-width="320"
            :max-width="860"
            :disabled="paperShotMode"
          >
            <div class="chart-card compact-chart">
              <div class="chart-title panel-title-row">
                <span>{{ metricLabel(chart.metric) }} @{{ chart.k }}</span>
                <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="360">
                  <template #reference>
                    <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
                  </template>
                  <div class="tip-pop-content">{{ metricExplain(chart.metric, chart.k) }}</div>
                </el-popover>
              </div>
              <div class="bar-list">
                <div class="bar-row" v-for="row in chart.values" :key="row.algorithm">
                  <div class="bar-name">{{ row.label }}</div>
                  <div class="bar-track">
                    <div class="bar-fill" :style="{ width: `${Math.min(100, Math.max(0, Number(row.value) * 100))}%` }"></div>
                  </div>
                  <div class="bar-value">{{ Number(row.value).toFixed(4) }}</div>
                </div>
              </div>
            </div>
          </ResizableWidthPanel>
        </div>

        <ResizableWidthPanel
          v-if="timeChart.length"
          class="chart-card-shell mt-12"
          panel-id="time-chart-panel"
          :storage-key="analyticsWidthStorageKey"
          :default-width="analyticsWidthPresets.timeChart"
          :min-width="420"
          :max-width="980"
          :disabled="paperShotMode"
        >
          <div class="chart-card">
            <div class="chart-title panel-title-row">
              <span>训练/推理耗时对比（毫秒）</span>
              <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="340">
                <template #reference>
                  <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
                </template>
                <div class="tip-pop-content">训练耗时是模型准备阶段花的时间；推理耗时是给一批用户生成推荐结果花的时间。单位是毫秒(ms)。</div>
              </el-popover>
            </div>
            <el-table :data="timeChart" size="small" border>
              <el-table-column prop="label" label="算法" min-width="200" />
              <el-table-column prop="train_cost_ms" width="140">
                <template #header>
                  <div class="table-head-with-tip">
                    <span>训练耗时(ms)</span>
                    <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="260">
                      <template #reference><el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button></template>
                      <div class="tip-pop-content">训练模型所花时间，越小表示模型准备越快。</div>
                    </el-popover>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="infer_cost_ms" width="140">
                <template #header>
                  <div class="table-head-with-tip">
                    <span>推理耗时(ms)</span>
                    <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="280">
                      <template #reference><el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button></template>
                      <div class="tip-pop-content">生成推荐结果所花时间，越小表示线上响应更快。</div>
                    </el-popover>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </ResizableWidthPanel>

        <div class="mt-12">
        <div class="chart-title panel-title-row">
          <span>指标明细（各算法 / 各K）</span>
          <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="360">
            <template #reference>
              <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
            </template>
            <div class="tip-pop-content">这里把每种算法在不同K值下的指标都列出来。K表示“给每个用户推荐前K个商品”。</div>
          </el-popover>
        </div>
        <div v-for="row in metricTableRows" :key="row.algorithm + row.k" class="metric-line">
          <span>{{ row.algorithmLabel }} @{{ row.k }}</span>
          <span>Recall {{ row.recall }}</span>
          <span>Precision {{ row.precision }}</span>
          <span>NDCG {{ row.ndcg }}</span>
          <span>HitRate {{ row.hit_rate }}</span>
          <span>Coverage {{ row.coverage }}</span>
        </div>
      </div>

      <div class="mt-12" v-if="lineChartSeries.length">
        <div class="chart-title panel-title-row">
          <span>指标随 K 变化趋势（折线图）</span>
          <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="360">
            <template #reference>
              <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
            </template>
            <div class="tip-pop-content">看每种算法在不同推荐数量（K）下表现怎么变化。这样能看出算法在“推荐少一些”或“推荐多一些”时是否稳定。</div>
          </el-popover>
        </div>
        <div class="resizable-flow line-flow">
          <ResizableWidthPanel
            v-for="lc in lineChartSeries"
            :key="lc.metric"
            class="chart-card-shell"
            :panel-id="`line-chart-${lc.metric}`"
            :storage-key="analyticsWidthStorageKey"
            :default-width="analyticsWidthPresets.lineChart"
            :min-width="360"
            :max-width="980"
            :disabled="paperShotMode"
          >
            <div class="chart-card">
              <div class="chart-title panel-title-row">
                <span>{{ metricLabel(lc.metric) }}-K 曲线</span>
                <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="360">
                  <template #reference>
                    <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
                  </template>
                  <div class="tip-pop-content">{{ metricExplain(lc.metric, 'K') }}</div>
                </el-popover>
              </div>
              <svg class="line-svg" viewBox="0 0 420 220" preserveAspectRatio="none">
                <line x1="40" y1="20" x2="40" y2="180" class="axis" />
                <line x1="40" y1="180" x2="390" y2="180" class="axis" />
                <g v-for="tick in [0,0.25,0.5,0.75,1]" :key="`${lc.metric}-${tick}`">
                  <line x1="40" :y1="180 - tick*160" x2="390" :y2="180 - tick*160" class="grid-line" />
                  <text x="8" :y="184 - tick*160" class="tick">{{ tick.toFixed(2) }}</text>
                </g>
                <g v-for="k in lc.ks" :key="`${lc.metric}-k-${k}`">
                  <text :x="xForK(lc.ks, k)" y="200" class="tick">{{ k }}</text>
                </g>
                <g v-for="s in lc.series" :key="`${lc.metric}-${s.algorithm}`">
                  <polyline :points="polylinePoints(lc.ks, s.values)" :class="['line-path', `line-${s.algorithm}`]" fill="none" />
                  <circle
                    v-for="(v, idx) in s.values"
                    :key="`${s.algorithm}-${idx}`"
                    :cx="xForIndex(lc.ks.length, idx)"
                    :cy="yForVal(v)"
                    r="3"
                    :class="['line-dot', `line-${s.algorithm}`]"
                  />
                </g>
              </svg>
              <div class="line-legend">
                <span v-for="s in lc.series" :key="s.algorithm" class="legend-item" :title="s.label">
                  <i :class="['legend-line', `line-${s.algorithm}`]"></i>
                  <span class="legend-text">{{ shortAlgorithmLabel(s.algorithm) }}</span>
                </span>
              </div>
            </div>
          </ResizableWidthPanel>
        </div>
      </div>

      <div class="mt-12" v-if="paramLineCharts.length">
        <div class="chart-title panel-title-row">
          <span>参数敏感性实验（折线图）</span>
          <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="360">
            <template #reference>
              <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
            </template>
            <div class="tip-pop-content">在同一批真实行为数据上，只修改算法参数（比如邻居数、因子数），观察指标变化，帮助你解释“参数怎么选”。</div>
          </el-popover>
        </div>
        <div class="resizable-flow line-flow compact">
          <ResizableWidthPanel
            v-for="lc in paramLineCharts"
            :key="lc.key"
            class="chart-card-shell"
            :panel-id="`param-chart-${lc.key}`"
            :storage-key="analyticsWidthStorageKey"
            :default-width="analyticsWidthPresets.lineChart"
            :min-width="360"
            :max-width="980"
            :disabled="paperShotMode"
          >
            <div class="chart-card compact-chart">
              <div class="chart-title panel-title-row">
                <span>{{ lc.title }}</span>
                <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="340">
                  <template #reference>
                    <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
                  </template>
                  <div class="tip-pop-content">{{ paramChartExplain(lc.title) }}</div>
                </el-popover>
              </div>
              <svg class="line-svg compact" viewBox="0 0 420 220" preserveAspectRatio="none">
                <line x1="40" y1="20" x2="40" y2="180" class="axis" />
                <line x1="40" y1="180" x2="390" y2="180" class="axis" />
                <g v-for="tick in [0,0.25,0.5,0.75,1]" :key="`${lc.key}-${tick}`">
                  <line x1="40" :y1="180 - tick*160" x2="390" :y2="180 - tick*160" class="grid-line" />
                  <text x="8" :y="184 - tick*160" class="tick">{{ tick.toFixed(2) }}</text>
                </g>
                <g v-for="x in lc.xs" :key="`${lc.key}-x-${x}`">
                  <text :x="xForIndex(lc.xs.length, lc.xs.indexOf(x))" y="200" class="tick">{{ x }}</text>
                </g>
                <g v-for="s in lc.series" :key="`${lc.key}-${s.algorithm}`">
                  <polyline :points="polylinePointsByXs(lc.xs, s.ys)" :class="['line-path', `line-${s.algorithm}`]" fill="none" />
                  <circle v-for="(v, idx) in s.ys" :key="`${lc.key}-${s.algorithm}-${idx}`" :cx="xForIndex(lc.xs.length, idx)" :cy="yForVal(v)" r="3" :class="['line-dot', `line-${s.algorithm}`]" />
                </g>
              </svg>
              <div class="line-legend">
                <span v-for="s in lc.series" :key="`${lc.key}-${s.algorithm}`" class="legend-item" :title="s.label">
                  <i :class="['legend-line', `line-${s.algorithm}`]"></i>
                  <span class="legend-text">{{ shortAlgorithmLabel(s.algorithm) }}</span>
                </span>
              </div>
            </div>
          </ResizableWidthPanel>
        </div>
      </div>

      <div class="mt-12" v-if="dataScaleLineCharts.length">
        <div class="chart-title panel-title-row">
          <span>数据规模影响实验（折线图）</span>
          <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="360">
            <template #reference>
              <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
            </template>
            <div class="tip-pop-content">用同一批真实数据按比例抽取训练行为，看看数据多或少时，各算法效果怎么变化。这能说明算法对数据量是否敏感。</div>
          </el-popover>
        </div>
        <div class="resizable-flow line-flow compact">
          <ResizableWidthPanel
            v-for="lc in dataScaleLineCharts"
            :key="lc.key"
            class="chart-card-shell"
            :panel-id="`data-scale-chart-${lc.key}`"
            :storage-key="analyticsWidthStorageKey"
            :default-width="analyticsWidthPresets.lineChart"
            :min-width="360"
            :max-width="980"
            :disabled="paperShotMode"
          >
            <div class="chart-card compact-chart">
              <div class="chart-title panel-title-row">
                <span>{{ lc.title }}</span>
                <el-popover v-if="!paperShotMode" placement="top" trigger="click" width="340">
                  <template #reference>
                    <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
                  </template>
                  <div class="tip-pop-content">横轴是用于训练的行为比例（不是用户比例），纵轴是对应指标。比例越高，说明给算法的学习信息越多。</div>
                </el-popover>
              </div>
              <svg class="line-svg compact" viewBox="0 0 420 220" preserveAspectRatio="none">
                <line x1="40" y1="20" x2="40" y2="180" class="axis" />
                <line x1="40" y1="180" x2="390" y2="180" class="axis" />
                <g v-for="tick in [0,0.25,0.5,0.75,1]" :key="`${lc.key}-${tick}`">
                  <line x1="40" :y1="180 - tick*160" x2="390" :y2="180 - tick*160" class="grid-line" />
                  <text x="8" :y="184 - tick*160" class="tick">{{ tick.toFixed(2) }}</text>
                </g>
                <g v-for="x in lc.xs" :key="`${lc.key}-x-${x}`">
                  <text :x="xForIndex(lc.xs.length, lc.xs.indexOf(x))" y="200" class="tick">{{ x }}</text>
                </g>
                <g v-for="s in lc.series" :key="`${lc.key}-${s.algorithm}`">
                  <polyline :points="polylinePointsByXs(lc.xs, s.ys)" :class="['line-path', `line-${s.algorithm}`]" fill="none" />
                  <circle v-for="(v, idx) in s.ys" :key="`${lc.key}-${s.algorithm}-${idx}`" :cx="xForIndex(lc.xs.length, idx)" :cy="yForVal(v)" r="3" :class="['line-dot', `line-${s.algorithm}`]" />
                </g>
              </svg>
              <div class="line-legend">
                <span v-for="s in lc.series" :key="`${lc.key}-${s.algorithm}`" class="legend-item" :title="s.label">
                  <i :class="['legend-line', `line-${s.algorithm}`]"></i>
                  <span class="legend-text">{{ shortAlgorithmLabel(s.algorithm) }}</span>
                </span>
              </div>
            </div>
          </ResizableWidthPanel>
        </div>
      </div>

      <div class="mt-12" v-if="algorithmAnalysisText">
        <div class="head">
          <div class="chart-title">算法分析（白话版）</div>
          <el-button v-if="!paperShotMode" size="small" @click="copyAlgorithmAnalysis">复制分析</el-button>
        </div>
        <el-input type="textarea" :rows="10" :model-value="algorithmAnalysisText" readonly />
      </div>

      <div class="mt-12" v-if="exportPayload.chapter_text">
        <div class="head">
          <div class="chart-title">第4章实验分析（自动草稿）</div>
          <el-button v-if="!paperShotMode" size="small" @click="copyChapterText">复制文本</el-button>
        </div>
        <el-input type="textarea" :rows="14" :model-value="exportPayload.chapter_text" readonly />
      </div>

      <div class="mt-12" v-if="!paperShotMode && exportPayload.files?.length">
        <div class="chart-title">导出文件</div>
        <div class="file-list">
          <a v-for="f in exportPayload.files" :key="f.path" :href="f.url" target="_blank" rel="noopener noreferrer">{{ f.name }}</a>
        </div>
      </div>
      </el-card>
    </ResizableWidthPanel>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { aimallApi } from '@/api/aimall';
import ResizableWidthPanel from '@/components/common/ResizableWidthPanel.vue';

const analyticsWidthStorageKey = 'aimall-recommendation-analytics-width';
const analyticsWidthPresets = {
  overviewCard: 1360,
  metricCard: 220,
  summaryPanel: 420,
  experimentsCard: 980,
  activeExperimentCard: 1360,
  chartCard: 420,
  timeChart: 560,
  lineChart: 560,
};

const overviewLoading = ref(false);
const running = ref(false);
const replaying = ref(false);
const exporting = ref(false);
const overview = ref<any>({});
const experiments = ref<any[]>([]);
const activeExperiment = ref<any | null>(null);
const exportPayload = ref<any>({});
const paperShotMode = ref(false);

const overviewCards = computed(() => {
  const d = overview.value?.data_summary || {};
  return [
    { label: '总行为数', value: d.total_behaviors ?? 0, help: '当前真实行为轨迹总条数（已自动排除实验回放模拟行为）。' },
    { label: '商品行为数（真实）', value: d.product_behaviors ?? 0, help: '真实行为里，目标对象是商品的行为总次数（如浏览商品、加入购物车、购买）。' },
    { label: '建模行为数', value: d.model_product_behaviors ?? d.product_behaviors ?? 0, help: '真正参与推荐算法建模计算的商品行为数。会受行为权重配置影响（某些行为权重设为0时可能不计入）。' },
    { label: '用户-商品交互', value: d.interactions ?? 0, help: '去重后的“用户-商品”交互对数量。一个用户反复看同一商品，仍然只算1个交互对。' },
    { label: '活跃用户数', value: d.active_users ?? 0, help: '在当前真实行为数据里，至少产生过一次商品相关行为的用户数量。' },
    { label: '活跃商品数', value: d.active_products ?? 0, help: '在当前真实行为数据里，至少被一个用户产生过商品相关行为的商品数量。' },
    { label: '数据稀疏度', value: d.sparsity ?? 0, help: '衡量用户-商品矩阵有多“稀”。越接近1表示大部分用户没有和大部分商品发生行为，推荐会更难做。' },
  ];
});

const behaviorRows = computed(() => {
  const data = overview.value?.data_summary?.behavior_type_distribution || {};
  const labelMap: Record<string, string> = {
    SEARCH: '搜索',
    CLICK_CATEGORY: '点击分类',
    VIEW_PRODUCT: '浏览商品',
    ADD_TO_CART: '加入购物车',
    PURCHASE: '购买',
  };
  return Object.keys(data).map((k) => ({ type: labelMap[k] || k, count: data[k] }));
});

const metricCharts = computed(() => activeExperiment.value?.chart_payload?.metricCharts || []);
const timeChart = computed(() => activeExperiment.value?.chart_payload?.timeChart || []);
const metricTableRows = computed(() => {
  const rows: any[] = [];
  const metrics = activeExperiment.value?.metrics_summary || {};
  Object.keys(metrics).forEach((alg) => {
    const item = metrics[alg];
    const mk = item.metrics_by_k || {};
    Object.keys(mk).forEach((k) => rows.push({ algorithm: alg, algorithmLabel: item.label || alg, k, ...mk[k] }));
  });
  return rows;
});
const lineChartSeries = computed(() => {
  const metrics = activeExperiment.value?.metrics_summary || {};
  const metricNames = ['recall', 'precision', 'ndcg', 'hit_rate', 'coverage'];
  return metricNames.map((metric) => {
    const kSet = new Set<number>();
    Object.values(metrics).forEach((p: any) => Object.keys(p?.metrics_by_k || {}).forEach((k) => kSet.add(Number(k))));
    const ks = Array.from(kSet).filter((x) => Number.isFinite(x)).sort((a, b) => a - b);
    const series = Object.keys(metrics).map((alg) => ({
      algorithm: alg,
      label: metrics[alg]?.label || alg,
      values: ks.map((k) => Number(metrics[alg]?.metrics_by_k?.[String(k)]?.[metric] ?? 0)),
    }));
    return { metric, ks, series };
  }).filter((x) => x.ks.length && x.series.length);
});
const paramLineCharts = computed(() => {
  const groups = activeExperiment.value?.chart_payload?.parameterSensitivityCharts || [];
  const rows: any[] = [];
  groups.forEach((g: any) => {
    (g.series || []).forEach((s: any) => {
      rows.push({
        key: `${g.algorithm}-${s.metric}`,
        title: `${g.label} - ${metricLabel(s.metric)}（${g.x_label}）`,
        xs: s.xs || [],
        series: [{ algorithm: g.algorithm, label: g.label, ys: s.ys || [] }],
      });
    });
  });
  return rows;
});
const dataScaleLineCharts = computed(() => {
  const groups = activeExperiment.value?.chart_payload?.dataScaleCharts || [];
  return groups.map((g: any) => ({
    key: `scale-${g.metric}`,
    title: `训练行为比例 vs ${metricLabel(g.metric)}@10`,
    xs: (g.series?.[0]?.xs || []).map((x: number) => Number((x * 100).toFixed(0))),
    series: (g.series || []).map((s: any) => ({
      algorithm: s.algorithm,
      label: s.label,
      ys: s.ys || [],
    })),
  }));
});
const algorithmAnalysisText = computed(() => {
  const ms = activeExperiment.value?.metrics_summary || {};
  const algs = Object.keys(ms);
  if (!algs.length) return '';
  const metricAt = (alg: string, metric: string, k = '10') => Number(ms?.[alg]?.metrics_by_k?.[k]?.[metric] ?? 0);
  const labels = (alg: string) => ms?.[alg]?.label || alg;
  const pickBest = (metric: string) => algs.slice().sort((a, b) => metricAt(b, metric) - metricAt(a, metric))[0];
  const bestRecall = pickBest('recall');
  const bestNdcg = pickBest('ndcg');
  const bestCoverage = pickBest('coverage');
  const fastestTrain = algs.slice().sort((a, b) => Number(ms[a]?.train_cost_ms ?? 0) - Number(ms[b]?.train_cost_ms ?? 0))[0];
  const fastestInfer = algs.slice().sort((a, b) => Number(ms[a]?.infer_cost_ms ?? 0) - Number(ms[b]?.infer_cost_ms ?? 0))[0];
  const lines: string[] = [];
  lines.push('1. 本次实验使用同一批真实行为轨迹数据对 UserCF、ItemCF、ALS 进行离线对比，因此结果具备可比性。');
  lines.push(`2. 在推荐“找全用户可能喜欢商品”的能力上（Recall@10），${labels(bestRecall)}表现最好（${metricAt(bestRecall, 'recall').toFixed(4)}）。`);
  lines.push(`3. 在推荐排序质量上（NDCG@10），${labels(bestNdcg)}表现最好（${metricAt(bestNdcg, 'ndcg').toFixed(4)}），说明其把更相关商品排在前面的能力更强。`);
  lines.push(`4. 在推荐覆盖率上（Coverage@10），${labels(bestCoverage)}表现最好（${metricAt(bestCoverage, 'coverage').toFixed(4)}），说明它覆盖到的商品更广。`);
  lines.push(`5. 训练耗时最短的是${labels(fastestTrain)}（${Number(ms[fastestTrain]?.train_cost_ms ?? 0).toFixed(2)}ms），推理耗时最短的是${labels(fastestInfer)}（${Number(ms[fastestInfer]?.infer_cost_ms ?? 0).toFixed(2)}ms）。`);
  lines.push('6. 如果论文重点强调“可解释性”和“系统展示”，建议突出 UserCF/ItemCF 的推荐原因；如果重点强调“稀疏数据稳定性”和“综合效果”，建议突出 ALS。');
  lines.push('7. 最终线上推荐算法可按业务目标选择：追求召回/稳定性优先 ALS，追求解释性与实现简单优先 ItemCF 或 UserCF。');
  return lines.join('\n');
});

function metricLabel(metric: string) {
  return ({
    recall: 'Recall',
    precision: 'Precision',
    ndcg: 'NDCG',
    hit_rate: 'HitRate',
    coverage: 'Coverage',
  } as any)[metric] || metric;
}
function metricExplain(metric: string, k: string | number) {
  const kText = typeof k === 'number' ? `@${k}` : '';
  const map: Record<string, string> = {
    recall: `Recall${kText}：看“该算法有没有尽量把用户真正会喜欢的商品找出来”。数值越高，漏掉的越少。`,
    precision: `Precision${kText}：看“推荐出来的商品里，有多少是真正相关的”。数值越高，推荐更准。`,
    ndcg: `NDCG${kText}：不只看推对没推对，还看“好商品有没有排在前面”。越高说明排序质量越好。`,
    hit_rate: `HitRate${kText}：看每个用户的推荐列表里“至少命中一个”的比例。越高说明更容易让用户看到感兴趣的商品。`,
    coverage: `Coverage${kText}：看算法推荐覆盖到了多少不同商品。越高说明不容易总是只推荐少数热门商品。`,
  };
  return map[metric] || `${metric}${kText} 指标说明`;
}
function paramChartExplain(title: string) {
  if (title.includes('neighbor_k')) {
    return 'neighbor_k 可以理解为“参考多少个相似邻居”。值太小可能信息不够，值太大可能把不太相似的数据也混进来。';
  }
  if (title.includes('als_factors')) {
    return 'als_factors 可以理解为“模型用多少个潜在兴趣维度来描述用户和商品”。太小表达能力不足，太大可能计算更慢。';
  }
  return '这是参数变化对指标结果的影响图，用来解释参数选择依据。';
}
function formatCnTime(input?: string) {
  if (!input) return '-';
  const d = new Date(input);
  if (Number.isNaN(d.getTime())) return String(input);
  const parts = new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).formatToParts(d);
  const get = (t: string) => parts.find((p) => p.type === t)?.value || '00';
  return `${get('year')}年${get('month')}月${get('day')}日${get('hour')}:${get('minute')}:${get('second')}`;
}
function shortAlgorithmLabel(alg: string) {
  return ({ USER_CF: 'UserCF', ITEM_CF: 'ItemCF', ALS: 'ALS' } as any)[alg] || alg;
}
function xForIndex(total: number, idx: number) {
  if (total <= 1) return 215;
  return 40 + (idx * 350) / (total - 1);
}
function xForK(ks: number[], k: number) {
  const idx = ks.indexOf(k);
  return xForIndex(ks.length, Math.max(idx, 0));
}
function yForVal(v: number) {
  const clamped = Math.max(0, Math.min(1, Number(v) || 0));
  return 180 - clamped * 160;
}
function polylinePoints(ks: number[], vals: number[]) {
  return vals.map((v, idx) => `${xForIndex(ks.length, idx)},${yForVal(v)}`).join(' ');
}
function polylinePointsByXs(xs: number[], vals: number[]) {
  return vals.map((v, idx) => `${xForIndex(xs.length, idx)},${yForVal(v)}`).join(' ');
}

async function loadOverview() {
  overviewLoading.value = true;
  try {
    overview.value = await aimallApi.getRecommendationAnalysis();
  } catch (e: any) {
    ElMessage.error(e.message || '加载数据分析失败');
  } finally {
    overviewLoading.value = false;
  }
}

async function loadExperiments() {
  try {
    experiments.value = await aimallApi.getRecommendationExperiments();
  } catch (e: any) {
    ElMessage.error(e.message || '加载实验记录失败');
  }
}

async function runExperiment() {
  running.value = true;
  try {
    const res = await aimallApi.runRecommendationExperiment({ name: '推荐算法对比实验', top_ks: [5, 10, 20] });
    if (res.ok) ElMessage.success(res.message || '实验完成');
    else ElMessage.warning(res.message || '实验失败');
    await loadExperiments();
    if (res?.id) {
      activeExperiment.value = await aimallApi.getRecommendationExperimentDetail(res.id);
    }
    await loadOverview();
  } catch (e: any) {
    ElMessage.error(e.message || '运行实验失败');
  } finally {
    running.value = false;
  }
}

async function generateBehaviorReplay() {
  replaying.value = true;
  try {
    const res = await aimallApi.generateRecommendationBehaviorReplay({
      target_customers: 36,
      actions_per_customer: 40,
      seed: 20260408,
      clear_all_behaviors: 1,
    });
    ElMessage.success(`${res.message || '已生成'}（新增样本用户 ${res.customer_count ?? 0} 个，行为 ${res.created_behaviors ?? 0} 条）`);
    await loadOverview();
  } catch (e: any) {
    ElMessage.error(e.message || '生成实验行为失败');
  } finally {
    replaying.value = false;
  }
}

async function resetBehaviors() {
  try {
    await ElMessageBox.confirm(
      '确认清空当前所有用户行为轨迹吗？默认会同时清空购物车项、已生成推荐结果以及系统创建的论文样本用户，便于重新生成一套干净的实验数据。',
      '清空行为轨迹',
      { type: 'warning', confirmButtonText: '确认清空', cancelButtonText: '取消' },
    );
    const res = await aimallApi.resetRecommendationBehaviors({ clear_carts: 1, clear_recommendations: 1 });
    ElMessage.success(
      `已清空：行为${res.behaviors_deleted ?? 0}条，购物车${res.cart_items_deleted ?? 0}条，推荐${res.recommendations_deleted ?? 0}条，论文样本用户${res.generated_customers_deleted ?? 0}个`,
    );
    activeExperiment.value = null;
    exportPayload.value = {};
    await loadOverview();
  } catch (e: any) {
    if (e?.message && !String(e.message).toLowerCase().includes('cancel')) {
      ElMessage.error(e.message || '清空行为轨迹失败');
    }
  }
}

async function openExperiment(row: any) {
  try {
    activeExperiment.value = await aimallApi.getRecommendationExperimentDetail(row.id);
    exportPayload.value = {};
  } catch (e: any) {
    ElMessage.error(e.message || '加载实验详情失败');
  }
}

async function exportArtifacts() {
  if (!activeExperiment.value?.id) return;
  exporting.value = true;
  try {
    exportPayload.value = await aimallApi.exportRecommendationExperiment(activeExperiment.value.id);
    ElMessage.success('实验材料导出成功');
  } catch (e: any) {
    ElMessage.error(e.message || '导出失败');
  } finally {
    exporting.value = false;
  }
}

async function copyChapterText() {
  const text = exportPayload.value?.chapter_text || '';
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success('已复制实验分析草稿');
  } catch {
    ElMessage.warning('复制失败，请手动复制');
  }
}
async function copyAlgorithmAnalysis() {
  if (!algorithmAnalysisText.value) return;
  try {
    await navigator.clipboard.writeText(algorithmAnalysisText.value);
    ElMessage.success('已复制算法分析文本');
  } catch {
    ElMessage.warning('复制失败，请手动复制');
  }
}

async function loadAll() {
  await Promise.all([loadOverview(), loadExperiments()]);
}

async function clearExperiments() {
  try {
    await ElMessageBox.confirm('确认清空所有实验记录以及导出的图表/CSV文件吗？该操作不可恢复。', '清空确认', {
      type: 'warning',
      confirmButtonText: '确认清空',
      cancelButtonText: '取消',
    });
    const res = await aimallApi.clearRecommendationExperiments();
    ElMessage.success(`已清空实验记录（${res.deleted ?? 0}条）`);
    experiments.value = [];
    activeExperiment.value = null;
    exportPayload.value = {};
  } catch (e: any) {
    if (e?.message && !String(e.message).toLowerCase().includes('cancel')) {
      ElMessage.error(e.message || '清空失败');
    }
  }
}

onMounted(() => {
  try {
    const qs = new URLSearchParams(window.location.search);
    if (qs.get('paperShot') === '1') {
      paperShotMode.value = true;
      return;
    }
    paperShotMode.value = localStorage.getItem('aimall_paper_shot_mode') === '1';
  } catch {}
});

watch(paperShotMode, (v) => {
  try {
    localStorage.setItem('aimall_paper_shot_mode', v ? '1' : '0');
  } catch {}
});

loadAll();
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}
.page > * {
  max-width: 100%;
}
.paper-shot-mode :deep(.el-card__header) {
  padding-bottom: 10px;
}
.paper-shot-mode .head {
  align-items: center;
}
.mt-12 { margin-top: 12px; }
.head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.head-tip { color: #94a3b8; font-size: 12px; }
.paper-switch { margin-right: 4px; }
.scope-tip { margin-bottom: 10px; color: #64748b; font-size: 12px; }
.section-card-shell,
.metric-card-shell,
.panel-shell,
.chart-card-shell {
  max-width: 100%;
}
.section-card-shell :deep(.el-card),
.section-card-shell :deep(.el-card__body) {
  width: 100%;
}
.resizable-flow {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: stretch;
}
.metrics-flow {
  margin-bottom: 12px;
}
.metric-label-row,
.panel-title-row,
.table-head-with-tip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.inline-tip-btn {
  width: 16px;
  height: 16px;
  min-height: 16px;
  padding: 0;
  border-radius: 50%;
  font-weight: 700;
}
.tip-pop-content {
  color: #475569;
  font-size: 13px;
  line-height: 1.6;
  white-space: normal;
}
.metric-card,
.panel,
.chart-card {
  height: 100%;
  box-sizing: border-box;
}
.metric-card { background: #f8fbff; border: 1px solid #dbeafe; border-radius: 10px; padding: 10px; }
.metric-label { color: #64748b; font-size: 12px; }
.metric-value { color: #0f172a; font-weight: 700; margin-top: 6px; }
.panel {
  padding: 10px;
  border: 1px solid #dbeafe;
  border-radius: 10px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
}
.panel-title { font-weight: 600; color: #1e3a8a; margin-bottom: 8px; }
.chart-card { border: 1px solid #dbeafe; border-radius: 10px; padding: 10px; background: #f8fbff; }
.chart-title { font-weight: 600; color: #1e3a8a; margin-bottom: 8px; }
.bar-list { display: flex; flex-direction: column; gap: 8px; }
.bar-row { display: grid; grid-template-columns: minmax(120px, 210px) 1fr 80px; gap: 8px; align-items: center; }
.bar-name { color: #334155; font-size: 12px; }
.bar-track { height: 10px; background: #e2e8f0; border-radius: 999px; overflow: hidden; }
.bar-fill { height: 100%; background: linear-gradient(90deg, #60a5fa, #2563eb); }
.bar-value { text-align: right; font-variant-numeric: tabular-nums; color: #1e293b; font-size: 12px; }
.metric-line { display: flex; flex-wrap: wrap; gap: 14px; color: #334155; font-size: 13px; padding: 6px 0; border-bottom: 1px dashed #e2e8f0; }
.empty-state { color: #94a3b8; }
.file-list { display: flex; flex-wrap: wrap; gap: 10px; }
.file-list a {
  color: #1d4ed8;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 999px;
  padding: 6px 10px;
  text-decoration: none;
  font-size: 12px;
}
.file-list a:hover { background: #dbeafe; }
.compact-chart {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
}
.line-svg {
  width: 100%;
  height: 220px;
  display: block;
  background: #fff;
  border: 1px solid #dbeafe;
  border-radius: 8px;
  box-sizing: border-box;
}
.line-svg.compact { height: 210px; }
.axis { stroke: #94a3b8; stroke-width: 1; }
.grid-line { stroke: #e2e8f0; stroke-width: 1; stroke-dasharray: 2 2; }
.tick { fill: #64748b; font-size: 11px; }
.line-path { stroke-width: 2; }
.line-dot { stroke: #fff; stroke-width: 1; }
.line-USER_CF { stroke: #2563eb; fill: #2563eb; }
.line-ITEM_CF { stroke: #16a34a; fill: #16a34a; }
.line-ALS { stroke: #f59e0b; fill: #f59e0b; }
.line-legend { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px; }
.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #334155;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid #dbeafe;
}
.legend-text { font-weight: 600; }
.legend-line {
  position: relative;
  width: 18px;
  height: 2px;
  border-radius: 999px;
  display: inline-block;
}
.legend-line::after {
  content: '';
  position: absolute;
  right: -1px;
  top: 50%;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  transform: translateY(-50%);
  background: currentColor;
  box-shadow: 0 0 0 1px #fff inset;
}
.legend-line.line-USER_CF { background: #2563eb; color: #2563eb; }
.legend-line.line-ITEM_CF { background: #16a34a; color: #16a34a; }
.legend-line.line-ALS { background: #f59e0b; color: #f59e0b; }
@media (max-width: 1200px) {
  .page {
    align-items: stretch;
  }
  .bar-row {
    grid-template-columns: 1fr;
  }
  .bar-value {
    text-align: left;
  }
}
</style>
