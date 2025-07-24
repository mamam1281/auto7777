```tsx
import React from 'react';
import Header from './Header';
import GachaSpinner from './GachaSpinner';
import GachaResults from './GachaResults';
import Footer from './Footer';

// GachaPage Layout Modification
const GachaPage = () => {
    return (
        <div className="gacha-layout">
            <Header />
            <main className="gacha-content">
                <GachaSpinner />
                <GachaResults />
            </main>
            <Footer />
        </div>
    );
};

export default GachaPage;
```