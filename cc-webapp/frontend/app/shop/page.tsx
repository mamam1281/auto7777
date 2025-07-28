
"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { Coins, Gem, Gift, ShoppingCart } from "lucide-react";

const shopItems = [
  {
    id: 1,
    name: "프리미엄 젬 100개",
    description: "게임 내 프리미엄 젬 100개를 즉시 획득!",
    price: 1200,
    currency: "KRW",
    icon: <Gem className="w-7 h-7 text-pink-400" />,
    isBest: true
  },
  {
    id: 2,
    name: "코인 10,000개",
    description: "일반 코인 10,000개로 다양한 게임을 즐기세요.",
    price: 500,
    currency: "KRW",
    icon: <Coins className="w-7 h-7 text-yellow-300" />
  },
  {
    id: 3,
    name: "한정 패키지",
    description: "젬+코인+랜덤박스가 모두 포함된 한정 패키지!",
    price: 2500,
    currency: "KRW",
    icon: <Gift className="w-7 h-7 text-emerald-400" />,
    isHot: true
  }
];

export default function ShopPage() {
  const [selected, setSelected] = useState<number | null>(null);

  return (
    <div className="shop-dashboard w-full max-w-[420px] mx-auto min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
      <motion.header
        className="py-6 text-center relative z-20"
        initial={{ opacity: 0, y: -40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, ease: "easeOut" }}
      >
        <motion.h1
          className="text-2xl font-extrabold tracking-wide text-pink-400 drop-shadow-lg flex items-center justify-center gap-2"
          whileHover={{ scale: 1.03 }}
        >
          <ShoppingCart className="w-7 h-7 text-pink-400" />
          상점
        </motion.h1>
        <p className="mt-2 text-sm text-white/70">젬, 코인, 한정 패키지를 구매하고 더 많은 혜택을 누리세요!</p>
      </motion.header>
      <main className="flex-1 pb-8 px-3">
        <motion.div
          className="flex flex-col gap-5 mt-8"
          initial="hidden"
          animate="visible"
          variants={{
            visible: { transition: { staggerChildren: 0.12 } }
          }}
        >
          {shopItems.map((item, idx) => (
            <motion.div
              key={item.id}
              className={`relative rounded-xl bg-white/5 border border-white/10 p-5 flex items-center gap-4 shadow-lg backdrop-blur-md transition-all duration-200 ${selected === item.id ? "ring-2 ring-pink-400" : "hover:scale-[1.025]"}`}
              whileHover={{ y: -2, scale: 1.025 }}
              onClick={() => setSelected(item.id)}
              variants={{
                hidden: { opacity: 0, y: 20 },
                visible: { opacity: 1, y: 0 }
              }}
            >
              <div className="flex-shrink-0">
                {item.icon}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold text-white drop-shadow-md tracking-wide">{item.name}</span>
                  {item.isBest && <span className="ml-2 px-2 py-0.5 text-xs rounded bg-pink-400 text-white font-semibold animate-pulse">BEST</span>}
                  {item.isHot && <span className="ml-2 px-2 py-0.5 text-xs rounded bg-emerald-400 text-white font-semibold animate-pulse">HOT</span>}
                </div>
                <p className="text-sm text-white/70 mt-1">{item.description}</p>
              </div>
              <div className="flex flex-col items-end">
                <span className="text-xl font-bold text-pink-300">₩{item.price.toLocaleString()}</span>
                <button
                  className="mt-2 px-4 py-1.5 rounded-lg bg-pink-500 hover:bg-pink-600 text-white font-semibold text-sm shadow-md transition-all duration-150"
                  onClick={e => { e.stopPropagation(); alert('결제 기능은 곧 제공됩니다!'); }}
                >
                  구매하기
                </button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </main>
    </div>
  );
}
