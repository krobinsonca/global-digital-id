import React, { useState, useEffect } from 'react'

// Mock data - simulates API responses
const INITIAL_PORTFOLIO = {
  usd: 10000,
  btc: 0,
  eth: 0,
  bnb: 0,
}

const CRYPTO_DATA = [
  { symbol: 'BTC', name: 'Bitcoin', price: 66800, change24h: 2.34 },
  { symbol: 'ETH', name: 'Ethereum', price: 3450, change24h: 1.87 },
  { symbol: 'BNB', name: 'BNB', price: 580, change24h: -0.45 },
  { symbol: 'SOL', name: 'Solana', price: 145, change24h: 5.67 },
  { symbol: 'XRP', name: 'XRP', price: 0.62, change24h: -1.23 },
]

const TRADE_HISTORY = []

export default function CryptoTrader() {
  const [portfolio, setPortfolio] = useState(INITIAL_PORTFOLIO)
  const [holdings, setHoldings] = useState({})
  const [prices, setPrices] = useState(CRYPTO_DATA)
  const [history, setHistory] = useState(TRADE_HISTORY)
  const [selectedCoin, setSelectedCoin] = useState('BTC')
  const [tradeAmount, setTradeAmount] = useState('')
  const [activeTab, setActiveTab] = useState('trade')

  // Simulate price fluctuations
  useEffect(() => {
    const interval = setInterval(() => {
      setPrices(prev => prev.map(coin => ({
        ...coin,
        price: coin.price * (1 + (Math.random() - 0.5) * 0.002),
        change24h: coin.change24h + (Math.random() - 0.5) * 0.1
      })))
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const getPrice = (symbol) => prices.find(p => p.symbol === symbol)?.price || 0

  const getValue = (symbol) => (holdings[symbol] || 0) * getPrice(symbol)

  const totalValue = portfolio.usd + Object.entries(holdings).reduce((sum, [sym, amt]) => sum + amt * getPrice(sym), 0)

  const handleBuy = () => {
    const amount = parseFloat(tradeAmount)
    if (!amount || amount <= 0) return
    
    const price = getPrice(selectedCoin)
    const cost = amount * price
    
    if (cost > portfolio.usd) {
      alert('Insufficient USD balance!')
      return
    }

    setPortfolio(prev => ({ ...prev, usd: prev.usd - cost }))
    setHoldings(prev => ({ ...prev, [selectedCoin]: (prev[selectedCoin] || 0) + amount }))
    setHistory(prev => [{
      type: 'BUY',
      coin: selectedCoin,
      amount,
      price,
      time: new Date().toLocaleTimeString()
    }, ...prev].slice(0, 20))
    setTradeAmount('')
  }

  const handleSell = () => {
    const amount = parseFloat(tradeAmount)
    if (!amount || amount <= 0) return
    
    const price = getPrice(selectedCoin)
    
    if ((holdings[selectedCoin] || 0) < amount) {
      alert('Insufficient holdings!')
      return
    }

    const revenue = amount * price
    setPortfolio(prev => ({ ...prev, usd: prev.usd + revenue }))
    setHoldings(prev => ({ ...prev, [selectedCoin]: (prev[selectedCoin] || 0) - amount }))
    setHistory(prev => [{
      type: 'SELL',
      coin: selectedCoin,
      amount,
      price,
      time: new Date().toLocaleTimeString()
    }, ...prev].slice(0, 20))
    setTradeAmount('')
  }

  return (
    <div style={{ minHeight: '100vh', background: '#0d1117', padding: '20px', fontFamily: 'monospace' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', paddingBottom: '16px', borderBottom: '1px solid #21262d' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#58a6ff' }}>📈 Crypto Trader</h1>
          <p style={{ color: '#8b949e', fontSize: '12px' }}>Paper Trading Simulator</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '28px', fontWeight: 700, color: '#3fb950' }}>
            ${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </div>
          <div style={{ color: '#8b949e', fontSize: '12px' }}>Portfolio Value</div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
        {['trade', 'portfolio', 'history'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '10px 20px',
              background: activeTab === tab ? '#21262d' : 'transparent',
              color: activeTab === tab ? '#58a6ff' : '#8b949e',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              textTransform: 'capitalize',
              fontWeight: 600,
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 'trade' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          {/* Market List */}
          <div style={{ background: '#161b22', borderRadius: '12px', padding: '16px' }}>
            <h3 style={{ color: '#e6edf3', marginBottom: '16px' }}>Markets</h3>
            {prices.map(coin => (
              <div
                key={coin.symbol}
                onClick={() => setSelectedCoin(coin.symbol)}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '12px',
                  background: selectedCoin === coin.symbol ? '#21262d' : 'transparent',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  marginBottom: '4px',
                }}
              >
                <div>
                  <div style={{ color: '#e6edf3', fontWeight: 600 }}>{coin.symbol}</div>
                  <div style={{ color: '#8b949e', fontSize: '12px' }}>{coin.name}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ color: '#e6edf3' }}>${coin.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                  <div style={{ color: coin.change24h >= 0 ? '#3fb950' : '#f85149', fontSize: '12px' }}>
                    {coin.change24h >= 0 ? '↑' : '↓'} {Math.abs(coin.change24h).toFixed(2)}%
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Trade Panel */}
          <div style={{ background: '#161b22', borderRadius: '12px', padding: '16px' }}>
            <h3 style={{ color: '#e6edf3', marginBottom: '16px' }}>Trade {selectedCoin}</h3>
            
            <div style={{ marginBottom: '20px', padding: '12px', background: '#0d1117', borderRadius: '8px' }}>
              <div style={{ color: '#8b949e', fontSize: '12px', marginBottom: '4px' }}>Current Price</div>
              <div style={{ color: '#58a6ff', fontSize: '24px', fontWeight: 700 }}>
                ${getPrice(selectedCoin).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ color: '#8b949e', fontSize: '12px', marginBottom: '8px' }}>Amount ({selectedCoin})</div>
              <input
                type="number"
                value={tradeAmount}
                onChange={(e) => setTradeAmount(e.target.value)}
                placeholder="0.00"
                style={{
                  width: '100%',
                  padding: '12px',
                  background: '#0d1117',
                  border: '1px solid #30363d',
                  borderRadius: '8px',
                  color: '#e6edf3',
                  fontSize: '18px',
                  fontFamily: 'monospace',
                }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
              <button
                onClick={handleBuy}
                style={{
                  padding: '14px',
                  background: '#238636',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                BUY
              </button>
              <button
                onClick={handleSell}
                style={{
                  padding: '14px',
                  background: '#da3633',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                SELL
              </button>
            </div>

            <div style={{ padding: '12px', background: '#0d1117', borderRadius: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ color: '#8b949e' }}>USD Balance</span>
                <span style={{ color: '#e6edf3' }}>${portfolio.usd.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#8b949e' }}>{selectedCoin} Balance</span>
                <span style={{ color: '#e6edf3' }}>{(holdings[selectedCoin] || 0).toFixed(6)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'portfolio' && (
        <div style={{ background: '#161b22', borderRadius: '12px', padding: '16px' }}>
          <h3 style={{ color: '#e6edf3', marginBottom: '16px' }}>Your Holdings</h3>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '16px', background: '#0d1117', borderRadius: '8px', marginBottom: '12px' }}>
            <span style={{ color: '#8b949e' }}>USD</span>
            <span style={{ color: '#e6edf3', fontWeight: 600 }}>${portfolio.usd.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
          </div>

          {prices.map(coin => (
            <div key={coin.symbol} style={{ display: 'flex', justifyContent: 'space-between', padding: '16px', background: '#0d1117', borderRadius: '8px', marginBottom: '8px' }}>
              <div>
                <span style={{ color: '#e6edf3', fontWeight: 600 }}>{coin.symbol}</span>
                <span style={{ color: '#8b949e', marginLeft: '12px' }}>{(holdings[coin.symbol] || 0).toFixed(6)}</span>
              </div>
              <div style={{ color: '#3fb950' }}>${getValue(coin.symbol).toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'history' && (
        <div style={{ background: '#161b22', borderRadius: '12px', padding: '16px' }}>
          <h3 style={{ color: '#e6edf3', marginBottom: '16px' }}>Trade History</h3>
          
          {history.length === 0 ? (
            <div style={{ color: '#8b949e', textAlign: 'center', padding: '40px' }}>No trades yet</div>
          ) : (
            history.map((trade, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', borderBottom: '1px solid #21262d' }}>
                <div>
                  <span style={{ color: trade.type === 'BUY' ? '#3fb950' : '#f85149', fontWeight: 600, marginRight: '12px' }}>
                    {trade.type}
                  </span>
                  <span style={{ color: '#e6edf3' }}>{trade.amount.toFixed(4)} {trade.coin}</span>
                </div>
                <div style={{ color: '#8b949e', fontSize: '12px' }}>
                  ${trade.price.toLocaleString()} • {trade.time}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Status Bar */}
      <div style={{ marginTop: '24px', padding: '12px', background: '#161b22', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#8b949e' }}>
        <span>🔄 Paper Trading Mode</span>
        <span>Prices update every 3s</span>
        <span>💰 Starting balance: $10,000</span>
      </div>
    </div>
  )
}
