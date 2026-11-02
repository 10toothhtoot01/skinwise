import {ArrowUpRight, Palette} from 'lucide-react';

type PaletteProduct = {id: string; name: string; color: string};

/** The palette uses entered colors; the still life is decorative, never a preview. */
export default function StudioIntro({products, sample}: {products: PaletteProduct[]; sample: boolean}) {
  return (
    <section className="studio-intro" aria-labelledby="studio-title">
      <div className="studio-intro-copy">
        <h1 id="studio-title">A look you can plan with what you own.</h1>
        <p>A little less guesswork. Start with your makeup, make room for your time, and find a combination you want to wear.</p>
        <div className="studio-intro-actions">
          <a className="planner-primary-link" href="#occasion">Plan my look <ArrowUpRight size={17}/></a>
          <a className="studio-secondary-link" href="#kit">Explore my kit <Palette size={17}/></a>
        </div>
        <p className="studio-intro-note">Planning is free. YouCam previews are optional, illustrative, and cost 1 API unit each.</p>
      </div>
      <aside className="studio-palette" aria-label="Your collection palette">
        <div className="studio-still-life" aria-hidden="true">
          <div className="planner-art-compact"><div className="planner-art-mirror"/><div className="planner-art-powder"/></div>
          <div className="planner-art-lipstick"><i/><b/></div>
        </div>
        <div className="studio-palette-content">
          <div className="studio-palette-label"><Palette size={17}/><span>{sample?'Your fictional sample palette':'Your collection, in color'}</span></div>
          {products.length > 0 ? <>
            <div className="studio-swatches">{products.map(product=><a key={product.id} href="#kit" title={product.name} aria-label={`See ${product.name} in your kit`} style={{backgroundColor:product.color}}/>)}</div>
            <p>{products.length} {products.length===1?'product':'products'} in your kit. Colors are approximate.</p>
          </> : <p>Add your first product and your palette will take shape here.</p>}
        </div>
      </aside>
    </section>
  );
}
