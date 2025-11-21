import React, { useRef, useState, useEffect } from "react";

function Confetti({ show }) {
  const ref = useRef();
  useEffect(() => {
    if (!show) return;
    const confetti = ref.current;
    confetti.innerHTML = '';
    const colors = [
      '#ffe066', '#ffb366', '#ff6666', '#fff', '#f357a8', '#7b2ff2', '#ffecb3',
      '#4dd599', '#00cfff', '#ffb3e6', '#ffde59', '#ff914d', '#ff5757', '#a259f7', '#f7c873', '#f7a6b9', '#b2f7ef', '#f7e6a6'
    ];
    for (let i = 0; i < 60; i++) {
      const el = document.createElement('div');
      el.style.position = 'absolute';
      el.style.background = colors[Math.floor(Math.random() * colors.length)];
      el.style.left = Math.random() * 100 + '%';
      el.style.top = (Math.random() * 10 - 5) + 'vh';
      el.style.width = (8 + Math.random() * 10) + 'px';
      el.style.height = (12 + Math.random() * 14) + 'px';
      el.style.opacity = 0.7 + Math.random() * 0.3;
      el.style.borderRadius = (Math.random() > 0.5 ? '50%' : '3px');
      el.style.transform = `rotate(${Math.random()*360}deg)`;
      el.style.transition = 'all 1.2s cubic-bezier(.4,2,.6,1)';
      confetti.appendChild(el);
      setTimeout(()=>{
        el.style.top = (parseFloat(el.style.top)+10+Math.random()*10)+'%';
        el.style.opacity = 0;
      }, 100);
    }
    setTimeout(()=>{if(confetti) confetti.innerHTML='';}, 1400);
  }, [show]);
  return <div ref={ref} style={{position:'fixed',top:0,left:0,width:'100vw',height:'100vh',pointerEvents:'none',zIndex:10001}} />;
}

function AdConfetti({ show }) {
  const ref = useRef();
  useEffect(() => {
    if (!show) return;
    const adConfetti = ref.current;
    adConfetti.innerHTML = '';
    const emojis = ['🎉','🎊','🎄','🎁','❄️','🧦','🪅','✨'];
    for (let i = 0; i < 18; i++) {
      const el = document.createElement('div');
      el.textContent = emojis[Math.floor(Math.random()*emojis.length)];
      el.style.position = 'absolute';
      el.style.left = Math.random()*95 + '%';
      el.style.top = Math.random()*80 + '%';
      el.style.fontSize = (28 + Math.random()*16) + 'px';
      el.style.opacity = 0.85;
      el.style.transition = 'all 1.2s cubic-bezier(.4,2,.6,1)';
      adConfetti.appendChild(el);
      setTimeout(()=>{
        el.style.top = (parseFloat(el.style.top)+10+Math.random()*10)+'%';
        el.style.opacity = 0;
      }, 100);
    }
    setTimeout(()=>{if(adConfetti) adConfetti.innerHTML='';}, 1400);
  }, [show]);
  return <div ref={ref} style={{position:'absolute',top:0,left:0,width:'100%',height:'100%',pointerEvents:'none',zIndex:10}} />;
}

export default function GamificationGame({ onClose, align }) {
  const [step, setStep] = useState('start');
  const [sliderValue, setSliderValue] = useState(50);
  const [sliderInterval, setSliderInterval] = useState(null);
  const [sliderDir, setSliderDir] = useState(1);
  const [showConfetti, setShowConfetti] = useState(false);
  const [showAdConfetti, setShowAdConfetti] = useState(false);
  const [showWin, setShowWin] = useState(false);
  const [showFail, setShowFail] = useState(false);
  const [showBalloonWin, setShowBalloonWin] = useState(false);
  const [balloonDiscount, setBalloonDiscount] = useState(0);
  const [showBadge, setShowBadge] = useState(false);
  // Balloon game state
  const [balloons, setBalloons] = useState([]);
  const [popped, setPopped] = useState(0);
  const [plusN, setPlusN] = useState([]);

  // Show slider immediately when game starts
  useEffect(() => {
    if (align === 'bottom' && step === 'start') {
      setStep('slider');
    }
    // eslint-disable-next-line
  }, [align, step]);

  // Animate slider
  useEffect(() => {
    if (step !== 'slider') return;
    let value = sliderValue;
    let dir = sliderDir;
    const interval = setInterval(() => {
      value += dir * 2;
      if (value >= 100) { value = 100; dir = -1; }
      else if (value <= 0) { value = 0; dir = 1; }
      setSliderValue(value);
      setSliderDir(dir);
    }, 18);
    setSliderInterval(interval);
    return () => clearInterval(interval);
    // eslint-disable-next-line
  }, [step]);

  // Balloon game logic
  useEffect(() => {
    if (step !== 'balloon') return;
    // Init balloons
    let arr = [];
    for (let i = 0; i < 7; i++) {
      arr.push({
        id: i,
        left: (10+Math.random()*80)+"%",
        top: (10+Math.random()*70)+"%",
        color: ["#ffb366","#ffe066","#f357a8","#7b2ff2","#4dd599","#ff6666","#00cfff"][i%7],
        popped: false
      });
    }
    setBalloons(arr);
    setBalloonDiscount(0);
    setPopped(0);
    setPlusN([]);
  }, [step]);

  function handleSliderSubmit() {
    clearInterval(sliderInterval);
    if (sliderValue >= 20 && sliderValue <= 60) {
      setShowConfetti(true);
      setShowWin(true);
      setTimeout(() => setShowWin(false), 2600);
      setTimeout(() => setShowConfetti(false), 4700);
      setShowBadge(true);
      setStep('done');
    } else if (sliderValue >= 61 && sliderValue <= 90) {
      setStep('balloon');
    } else {
      setShowFail(true);
      setTimeout(() => setShowFail(false), 2200);
      setStep('done');
    }
  }

  function popBalloon(idx) {
    if (balloons[idx].popped) return;
    let discount = Math.floor(Math.random()*5)+1;
    let newTotal = Math.min(balloonDiscount + discount, 10);
    let arr = balloons.slice();
    arr[idx].popped = true;
    setBalloons(arr);
    setBalloonDiscount(newTotal);
    setShowAdConfetti(true);
    setTimeout(() => setShowAdConfetti(false), 1200);
    setPlusN([...plusN, {id:idx, value:discount, left:arr[idx].left, top:arr[idx].top}]);
    setTimeout(() => setPlusN(pn => pn.filter(p => p.id !== idx)), 1100);
    let poppedCount = arr.filter(b => b.popped).length;
    setPopped(poppedCount);
    if (poppedCount === balloons.length) {
      setTimeout(() => {
        setShowBalloonWin(true);
        setShowBadge(true);
        setTimeout(() => setShowBalloonWin(false), 3500);
        setStep('done');
      }, 800);
    }
  }

  // The parent container should match the ad image size and border radius
  return (
    <div
      className="game-ad-overlay-container"
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        borderRadius: 32, // Match ad image
        overflow: 'hidden', // Prevent balloons/results from overflowing
        pointerEvents: step !== 'start' ? 'auto' : 'none', // FIXED: was isGameActive
        zIndex: 2,
      }}
    >
      <div
        className="game-overlay"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'transparent',
          boxShadow: 'none',
          borderRadius: 32,
          pointerEvents: step !== 'start' ? 'auto' : 'none', // FIXED: was isGameActive
        }}
      >
        <div
          className="slider-container"
          style={{
            background: 'transparent', // Remove any background from slider container
            boxShadow: 'none',
            borderRadius: 0,
            padding: 0,
            margin: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <button onClick={onClose} style={{position:'absolute',top:24,right:18,zIndex:20,background:'#fff',border:'none',borderRadius:16,padding:'4px 12px',fontWeight:600,cursor:'pointer',boxShadow:'0 2px 8px #0002'}}>✕</button>
          {step === 'slider' && (
            <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:16, width:'100%'}}>
              <div style={{fontWeight:600,marginBottom:8, color:'#7b2ff2'}}>Pick a number between 0 and 100</div>
              <div style={{
                background: '#27ae60',
                borderRadius: 32,
                padding: '18px 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 2px 12px #27ae6044',
                marginBottom: 8,
              }}>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={sliderValue}
                  className="slider christmas-slider"
                  style={{width:180, margin:'0 auto'}}
                  readOnly
                />
              </div>
              <button className="solid-btn" onClick={handleSliderSubmit} style={{marginTop:8}}>Submit</button>
            </div>
          )}
          {showConfetti && <Confetti show={showConfetti} />}
          {showAdConfetti && <AdConfetti show={showAdConfetti} />}
          {showWin && (
            <div style={{position:'fixed',top:0,left:0,right:0,bottom:0,display:'flex',alignItems:'center',justifyContent:'center',zIndex:10000}}>
              <div style={{background:'rgba(123,47,242,0.92)',color:'#fff',fontSize:'2.2rem',fontWeight:'bold',borderRadius:24,padding:'32px 48px',boxShadow:'0 4px 24px #7b2ff288',animation:'pop 1.2s'}}>
                Yaaay! <span style={{fontSize:'2.2rem'}}>🎉</span>
                <div style={{marginTop:18,fontSize:'1.5rem',color:'#ffe066',fontWeight:'bold'}}>20% OFF code: <b>WIN20</b></div>
              </div>
            </div>
          )}
          {showFail && (
            <div style={{position:'fixed',top:0,left:0,right:0,bottom:0,display:'flex',alignItems:'center',justifyContent:'center',zIndex:10000}}>
              <div style={{background:'rgba(220,38,38,0.92)',color:'#fff',fontSize:'2.2rem',fontWeight:'bold',borderRadius:24,padding:'32px 48px',boxShadow:'0 4px 24px #b91c1c88',animation:'pop 1.2s'}}>
                Oops!<div style={{marginTop:18,fontSize:'1.5rem',color:'#ffe066',fontWeight:'bold'}}>Maybe next time...</div>
              </div>
            </div>
          )}
          {step === 'balloon' && (
            <div style={{position:'absolute',left:0,top:0,width:'100%',height:'100%',background:'transparent',borderRadius:24,overflow:'hidden',zIndex:10}}>
              {balloons.map((b,i)=>(
                <div key={b.id} style={{
                  position:'absolute',
                  left:b.left,
                  top:b.top,
                  width:38,
                  height:48,
                  background:b.color,
                  borderRadius:'50% 50% 50% 50%/60% 60% 40% 40%',
                  boxShadow:'0 4px 16px #0002',
                  cursor:'pointer',
                  zIndex:5,
                  display:'flex',
                  alignItems:'flex-end',
                  justifyContent:'center',
                  pointerEvents:b.popped?'none':'auto',
                  opacity:b.popped?0.2:1,
                  transition:'transform 0.2s, opacity 0.2s',
                  animation: b.popped ? '' : `balloonFloat${i%3+1} 3.2s ease-in-out infinite alternate`,
                }} onClick={()=>popBalloon(i)}>
                  <div style={{width:2,height:18,background:'#aaa',marginBottom:-18,borderRadius:1}}></div>
                  {/* Confetti/cracker burst when popped */}
                  {b.popped && <span style={{position:'absolute',top:-18,left:10,fontSize:'1.5rem',pointerEvents:'none',animation:'crackerBurst 2.4s linear'}}>🎉</span>}
                </div>
              ))}
              {plusN.map(p=>(
                <div key={p.id} style={{position:'absolute',left:p.left,top:p.top,fontSize:'1.7rem',fontWeight:'bold',color:'#f357a8',textShadow:'0 2px 8px #fff, 0 1px 4px #f357a8',pointerEvents:'none',zIndex:50,animation:'plusN-bounce 1.1s cubic-bezier(.4,2,.6,1) forwards'}}>
                  +{p.value}
                </div>
              ))}
              <style>{`
                @keyframes balloonFloat1 {
                  0% { transform: translateY(0) scale(1); }
                  50% { transform: translateY(-18px) scale(1.04); }
                  100% { transform: translateY(0) scale(1); }
                }
                @keyframes balloonFloat2 {
                  0% { transform: translateY(0) scale(1); }
                  50% { transform: translateY(-12px) scale(1.07); }
                  100% { transform: translateY(0) scale(1); }
                }
                @keyframes balloonFloat3 {
                  0% { transform: translateY(0) scale(1); }
                  50% { transform: translateY(-24px) scale(1.03); }
                  100% { transform: translateY(0) scale(1); }
                }
                @keyframes crackerBurst {
                  0% { opacity: 0; transform: scale(0.5) rotate(-20deg); }
                  40% { opacity: 1; transform: scale(1.2) rotate(10deg); }
                  100% { opacity: 0; transform: scale(1.5) rotate(30deg); }
                }
              `}</style>
            </div>
          )}
          {showBalloonWin && (
            <div style={{position:'absolute',top:'50%',left:'50%',transform:'translate(-50%,-50%)',background:'linear-gradient(120deg,#fffbe6 0%,#ffe066 60%,#f357a8 100%)',color:'#7b2ff2',fontSize:'2.1rem',fontWeight:'bold',borderRadius:28,padding:'28px 44px 24px 44px',boxShadow:'0 6px 32px #7b2ff244, 0 1px 4px #0002',zIndex:40,textAlign:'center',display:'flex',flexDirection:'column',alignItems:'center',gap:12,border:'3px solid #fff',animation:'balloonWinPop 1.2s cubic-bezier(.4,2,.6,1) forwards'}}>
            <span style={{fontSize:'2.2rem',filter:'drop-shadow(0 2px 8px #f357a8cc)',animation:'crackerPop 1.2s cubic-bezier(.4,2,.6,1) infinite alternate'}}>🎉</span>
            <span style={{fontSize:'1.3rem',color:'#d72660',textShadow:'0 2px 8px #fff,0 1px 4px #f357a8'}}>You won <b style={{color:'#2ecc40'}}>{balloonDiscount}% OFF</b>!</span>
            <span style={{fontSize:'1.1rem',color:'#7b2ff2',background:'rgba(255,255,255,0.7)',borderRadius:12,padding:'4px 16px',marginTop:8,display:'inline-block',boxShadow:'0 2px 8px #ffe06688'}}>Code: <b>BALLOON{balloonDiscount}</b></span>
            <span style={{fontSize:'2.2rem',filter:'drop-shadow(0 2px 8px #f357a8cc)',animation:'crackerPop 1.2s cubic-bezier(.4,2,.6,1) infinite alternate'}}>🎄</span>
          </div>
          )}
          {showBadge && (
            <div style={{position:'absolute',top:18,right:18,background:'linear-gradient(90deg,#7b2ff2,#f357a8)',color:'#fff',fontSize:'0.95rem',fontWeight:'bold',borderRadius:14,padding:'5px 12px 5px 10px',boxShadow:'0 2px 8px #7b2ff233',zIndex:32,display:'flex',alignItems:'center',gap:6,opacity:1,transform:'scale(0.8)'}}>
              <span style={{marginRight:8,fontSize:'1.3em'}}>✔️</span>{step==='slider'?`20% Discount: WIN20`:`${balloonDiscount}% Discount: BALLOON${balloonDiscount}`}
            </div>
          )}
          <style>{`
            @keyframes plusN-bounce {
              0% { transform: translateY(0) scale(1); opacity: 1; }
              60% { transform: translateY(-32px) scale(1.18); opacity: 1; }
              100% { transform: translateY(-60px) scale(0.9); opacity: 0; }
            }
            @keyframes balloonWinPop {
              0% { opacity: 0; transform: translate(-50%, -50%) scale(0.7); }
              60% { opacity: 1; transform: translate(-50%, -50%) scale(1.08); }
              100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            }
            @keyframes crackerPop {
              0% { transform: scale(1) rotate(-10deg); }
              100% { transform: scale(1.18) rotate(10deg); }
            }
            @keyframes pop {
              0% { transform: scale(0.7); opacity: 0; }
              60% { transform: scale(1.15); opacity: 1; }
              100% { transform: scale(1); opacity: 1; }
            }
            .christmas-slider {
              background: #e0e0e0;
              border-radius: 8px;
              height: 10px;
            }
            .christmas-slider::-webkit-slider-thumb {
              background: radial-gradient(circle at 60% 40%, #fff 60%, #27ae60 100%);
              border: 3px solid #e74c3c;
            }
            .christmas-slider::-moz-range-thumb {
              background: radial-gradient(circle at 60% 40%, #fff 60%, #27ae60 100%);
              border: 3px solid #e74c3c;
            }
            .christmas-slider::-ms-thumb {
              background: radial-gradient(circle at 60% 40%, #fff 60%, #27ae60 100%);
              border: 3px solid #e74c3c;
            }
          `}</style>
        </div>
      </div>
    </div>
  );
}
