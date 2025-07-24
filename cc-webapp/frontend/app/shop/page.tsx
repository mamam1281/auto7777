import React from "react";

export default function ShopPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-[#0f0f23] to-[#1a1a2e] p-6 flex flex-col items-center">
      <h1 className="text-3xl font-bold text-white mb-6 drop-shadow-lg">상점 (Shop)</h1>
      <section className="w-full max-w-2xl bg-white/10 rounded-2xl shadow-lg p-8 flex flex-col gap-8">
        <div className="flex flex-col md:flex-row gap-6 items-center justify-between">
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-neon-purple-2 mb-2">프리미엄 젬</h2>
            <p className="text-white/80 mb-4">게임 내 다양한 혜택을 누릴 수 있는 프리미엄 젬을 구매하세요!</p>
            <button className="bg-gradient-to-r from-neon-purple-1 to-neon-purple-3 text-white px-6 py-2 rounded-lg shadow-md font-bold hover:scale-105 transition-transform">구매하기</button>
          </div>
          <div className="w-32 h-32 bg-gradient-to-br from-neon-purple-2 to-neon-purple-4 rounded-full flex items-center justify-center shadow-lg">
            <span className="text-5xl text-white font-extrabold">💎</span>
          </div>
        </div>
        <div className="flex flex-col md:flex-row gap-6 items-center justify-between">
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-game-gold mb-2">무료 코인</h2>
            <p className="text-white/80 mb-4">매일 무료 코인을 받아 다양한 게임을 즐겨보세요!</p>
            <button className="bg-game-gold text-black px-6 py-2 rounded-lg shadow-md font-bold hover:scale-105 transition-transform">받기</button>
          </div>
          <div className="w-32 h-32 bg-gradient-to-br from-game-gold to-game-success rounded-full flex items-center justify-center shadow-lg">
            <span className="text-5xl text-black font-extrabold">🪙</span>
          </div>
        </div>
      </section>
    </main>
  );
}
