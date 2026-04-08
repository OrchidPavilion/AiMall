<template>
  <el-card v-loading="loading">
    <template #header>
      <div class="head">
        <span>推荐设置</span>
        <el-space>
          <el-button @click="load">重置</el-button>
          <el-button type="primary" @click="save" :loading="saving">保存设置</el-button>
        </el-space>
      </div>
    </template>

    <el-form label-width="220px" class="form">
      <el-form-item>
        <template #label>
          <div class="label-with-help">
            <span>线上推荐算法（单选）</span>
            <el-popover placement="top" trigger="click" width="340">
              <template #reference>
                <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
              </template>
              <div class="tip-pop-content">这是商城真正给用户出推荐时使用的算法。可以把它理解成“推荐系统现在用哪种思路算结果”。选哪一个，会影响首页和后台里的推荐内容。</div>
            </el-popover>
          </div>
        </template>
        <el-radio-group v-model="form.online_algorithm">
          <el-radio-button label="USER_CF">基于用户的协同过滤</el-radio-button>
          <el-radio-button label="ITEM_CF">基于物品的协同过滤</el-radio-button>
          <el-radio-button label="ALS">ALS矩阵分解</el-radio-button>
        </el-radio-group>
        <div class="tip">该设置控制商城首页和管理后台“刷新推荐”使用的算法。论文实验对比会三种算法并行运行，不受此处限制。</div>
      </el-form-item>

      <el-form-item>
        <template #label>
          <div class="label-with-help">
            <span>TopN（线上推荐条数）</span>
            <el-popover placement="top" trigger="click" width="340">
              <template #reference>
                <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
              </template>
              <div class="tip-pop-content">表示每次最终给用户展示多少个推荐商品。数字越大，用户看到的推荐越多；数字越小，推荐列表会更短、更集中。</div>
            </el-popover>
          </div>
        </template>
        <el-input-number v-model="form.top_n" :min="1" :max="20" />
      </el-form-item>

      <el-form-item>
        <template #label>
          <div class="label-with-help">
            <span>邻居数 K（UserCF/ItemCF）</span>
            <el-popover placement="top" trigger="click" width="360">
              <template #reference>
                <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
              </template>
              <div class="tip-pop-content">可以理解成“参考多少个相似对象来做推荐”。在 UserCF 里，是参考多少个和当前用户相似的人；在 ItemCF 里，是参考多少个和当前商品相似的商品。太小信息可能不够，太大可能把不太相关的内容也算进去。</div>
            </el-popover>
          </div>
        </template>
        <el-input-number v-model="form.neighbor_k" :min="1" :max="100" />
      </el-form-item>

      <el-form-item>
        <template #label>
          <div class="label-with-help">
            <span>ALS 因子数</span>
            <el-popover placement="top" trigger="click" width="340">
              <template #reference>
                <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
              </template>
              <div class="tip-pop-content">可以把它理解成“模型用多少个隐藏维度去理解用户兴趣和商品特点”。数字越大，模型表达能力更强，但计算也会更重；数字太小，可能学不出足够细的偏好。</div>
            </el-popover>
          </div>
        </template>
        <el-input-number v-model="form.als_factors" :min="4" :max="64" />
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="label-with-help">
            <span>ALS 迭代次数</span>
            <el-popover placement="top" trigger="click" width="340">
              <template #reference>
                <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
              </template>
              <div class="tip-pop-content">表示模型要反复学习多少轮。轮数多一些，模型通常会学得更充分；但也会更慢。太少可能学不稳，太多可能收益不明显。</div>
            </el-popover>
          </div>
        </template>
        <el-input-number v-model="form.als_iterations" :min="2" :max="50" />
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="label-with-help">
            <span>ALS Alpha（隐式置信度）</span>
            <el-popover placement="top" trigger="click" width="360">
              <template #reference>
                <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
              </template>
              <div class="tip-pop-content">这个值决定模型“有行为的数据到底要看得多重”。数字越大，模型越会相信用户真实做过的行为，比如浏览、加购这些记录；数字太高时，模型可能会过度依赖已有行为。</div>
            </el-popover>
          </div>
        </template>
        <el-input-number v-model="form.als_alpha" :min="1" :max="100" />
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="label-with-help">
            <span>ALS 正则化</span>
            <el-popover placement="top" trigger="click" width="360">
              <template #reference>
                <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
              </template>
              <div class="tip-pop-content">这个值是防止模型“记死训练数据”的安全阀。值大一些，模型会更保守；值小一些，模型会更激进。简单理解，就是防止推荐结果只会背答案、不够泛化。</div>
            </el-popover>
          </div>
        </template>
        <el-input-number v-model="form.als_regularization" :min="0.01" :max="10" :step="0.01" :precision="2" />
      </el-form-item>

      <el-divider>行为权重（用于构建隐式反馈强度）</el-divider>
      <el-form-item>
        <template #label>
          <div class="label-with-help">
            <span>搜索 SEARCH</span>
            <el-popover placement="top" trigger="click" width="340">
              <template #reference>
                <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
              </template>
              <div class="tip-pop-content">表示“用户主动搜某类商品”这件事在推荐里占多大分量。分数越高，系统越会把搜索当成强兴趣信号。</div>
            </el-popover>
          </div>
        </template>
        <el-input-number v-model="form.behavior_weights.SEARCH" :min="0" :max="20" />
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="label-with-help">
            <span>点击分类 CLICK_CATEGORY</span>
            <el-popover placement="top" trigger="click" width="340">
              <template #reference>
                <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
              </template>
              <div class="tip-pop-content">表示“用户点进某个商品分类”这件事要给多少权重。它说明用户对某一大类商品有兴趣，但通常没有加购、下单那么强。</div>
            </el-popover>
          </div>
        </template>
        <el-input-number v-model="form.behavior_weights.CLICK_CATEGORY" :min="0" :max="20" />
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="label-with-help">
            <span>浏览商品 VIEW_PRODUCT</span>
            <el-popover placement="top" trigger="click" width="340">
              <template #reference>
                <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
              </template>
              <div class="tip-pop-content">表示“用户打开并查看某个商品详情”有多重要。这个动作通常比点分类更具体，说明用户已经对某件商品有明确关注。</div>
            </el-popover>
          </div>
        </template>
        <el-input-number v-model="form.behavior_weights.VIEW_PRODUCT" :min="0" :max="20" />
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="label-with-help">
            <span>加入购物车 ADD_TO_CART</span>
            <el-popover placement="top" trigger="click" width="340">
              <template #reference>
                <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
              </template>
              <div class="tip-pop-content">表示“用户把商品放进购物车”有多重要。这个动作通常最接近真实购买意向，所以一般会给更高权重。</div>
            </el-popover>
          </div>
        </template>
        <el-input-number v-model="form.behavior_weights.ADD_TO_CART" :min="0" :max="20" />
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="label-with-help">
            <span>购买 PURCHASE</span>
            <el-popover placement="top" trigger="click" width="360">
              <template #reference>
                <el-button class="inline-tip-btn" type="primary" text circle size="small">?</el-button>
              </template>
              <div class="tip-pop-content">表示“用户已经完成结算，真正买下商品”这个动作在推荐里要占多大分量。通常这是最强的兴趣信号，因为它不只是看看，而是真实下单。</div>
            </el-popover>
          </div>
        </template>
        <el-input-number v-model="form.behavior_weights.PURCHASE" :min="0" :max="20" />
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { aimallApi } from '@/api/aimall';

const loading = ref(false);
const saving = ref(false);
const form = reactive<any>({
  online_algorithm: 'ALS',
  top_n: 10,
  neighbor_k: 10,
  als_factors: 12,
  als_iterations: 8,
  als_alpha: 20,
  als_regularization: 0.1,
  behavior_weights: { SEARCH: 1, CLICK_CATEGORY: 1, VIEW_PRODUCT: 2, ADD_TO_CART: 4, PURCHASE: 6 },
});

async function load() {
  loading.value = true;
  try {
    const data = await aimallApi.getRecommendationSettings();
    Object.assign(form, data, {
      behavior_weights: { SEARCH: 1, CLICK_CATEGORY: 1, VIEW_PRODUCT: 2, ADD_TO_CART: 4, PURCHASE: 6, ...(data.behavior_weights || {}) },
    });
  } catch (e: any) {
    ElMessage.error(e.message || '加载设置失败');
  } finally {
    loading.value = false;
  }
}

async function save() {
  saving.value = true;
  try {
    await aimallApi.updateRecommendationSettings({
      ...form,
      behavior_weights: { ...form.behavior_weights },
    });
    ElMessage.success('推荐设置已保存');
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败');
  } finally {
    saving.value = false;
  }
}

load();
</script>

<style scoped>
.head { display: flex; align-items: center; justify-content: space-between; }
.form { max-width: 920px; }
.tip { margin-top: 8px; color: #64748b; font-size: 12px; line-height: 1.5; }
.label-with-help {
  display: inline-flex;
  align-items: center;
  gap: 6px;
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
  line-height: 1.65;
  white-space: normal;
}
</style>
