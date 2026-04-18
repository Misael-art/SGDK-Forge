//---------------------------------------------------------------------------

#include <vcl.h>
#include <stdio.h>
#pragma hdrstop
#include "UnitMain.h"
#include "UnitBankCHR.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TFormBankCHR *FormBankCHR;

extern bool openByFileDone;
const int CHR_4k=4096;
const int bankwin=8;

extern char tileViewTable[];
extern int palActive;
extern char chrSelected[];
extern unsigned char chrBank[];
extern int chrA_id[];
extern int chrB_id[];
extern int chrBanks;
AnsiString strList;
TRect curSelection;
TRect bnkSelection;
TRect bnkCursor;
TRect curCursor;
bool isBnkCursor=false;
bool curSetHover=false;
bool bnkSetHover=false;
bool clickSent=false;
//---------------------------------------------------------------------------
__fastcall TFormBankCHR::TFormBankCHR(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
void __fastcall TFormBankCHR::Draw(void)
{
	btnA->Down = FormMain->SpeedButtonChrBank1->Down;
	btnB->Down = FormMain->SpeedButtonChrBank2->Down;
	int x=0;
	int y=0;
	Image1     ->Picture->Bitmap->SetSize(128,128);
	Image2     ->Picture->Bitmap->SetSize(128,128);
	for(int i=0;i<256;i++)
	{
		//DrawTile(TPicture *pic,int x,int y,int tile,int pal,int tx,int ty,bool sel, bool efficientTarget, int inputScale, bool bIsNav, bool doubleWidth)
		FormMain->DrawTile(Image1->Picture,x,y,i,palActive,-1,-1,chrSelected[i],true,1,false,false);
		FormMain->DrawTile(Image2->Picture,x,y,i,palActive,-1,-1,chrSelected[i],true,1,false,false);


		x+=8;
		if(x>=128){	x=0; y+=8; }
	}

	isBnkCursor=false;
	FormMain->DrawSelection(Image1,curSelection,1,true,false);
	FormMain->DrawSelection(Image2,bnkSelection,1,false,false);

	if(!clickSent)
	{isBnkCursor=true;
	if(curSetHover)	FormMain->DrawSelection(Image1,curCursor,1,true,false);
	if(bnkSetHover) FormMain->DrawSelection(Image2,bnkCursor,1,false,false);
	isBnkCursor=false;
	}
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::MakeList(void)
{
	for(int i=0;i<chrBanks;i++)
	{
		strList=IntToHex(i,2)+"\t @ $"+IntToHex(i*4096,5);
		ListBox1->Items->Add(strList);
	}
    ListBox1->Selected[0]=true;
}
//---------------------------------------------------------------------------
void __fastcall TFormBankCHR::FormShow(TObject *Sender)
{
	Draw();	
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::FormCreate(TObject *Sender)
{
	Image1->Picture=new TPicture();
	Image1->Picture->Bitmap=new Graphics::TBitmap();
	Image1->Picture->Bitmap->PixelFormat=pf24bit;

	Image2->Picture=new TPicture();
	Image2->Picture->Bitmap=new Graphics::TBitmap();
	Image2->Picture->Bitmap->PixelFormat=pf24bit;
    Image2->Stretch=true;
	MakeList();

	int len;
	if(btn512b->Down) {len=2;}
	if(btn1k->Down)   {len=4;}
	if(btn2k->Down)   {len=8;}
	if(btn4k->Down)   {len=16;}

	//curSelection.Height(len*8);
	//curSelection.Top(0);
	curSelection = TRect(0, 0, 16, 0 + len);
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::SpeedButton1Click(TObject *Sender)
{
	int i,id, total;

	FormMain->SetUndo();

	id=ListBox1->ItemIndex;
	total=ListBox1->Items->Count-1;

	//push working
	for(i=0;i<bankwin;i++)
	{
		if (id>chrA_id[i]) chrA_id[i]+=bankwin;
		if (id>chrB_id[i]) chrB_id[i]+=bankwin;
	}
	for(i=total;i>id;--i)
	{
		memcpy(&chrBank[i*CHR_4k],&chrBank[(i-1)*CHR_4k],CHR_4k);
		//does anything else
		/*
		if(CheckMoveName->Checked){
			metaSpriteNames[i]	= metaSpriteNames[i-1];
		} */
	}

	memset(&chrBank[id*CHR_4k],0,CHR_4k);

	/*
	if(CheckMoveName->Checked){
		metaSpriteNames[id] = "unnamed";
	}

	if(metaSpriteActive<255) ++metaSpriteActive;

	FormMain->UpdateMetaSprite();

	Update();
	*/
	chrBanks++;
	ListBox1->Items->Insert(id,"new");
	//RefreshList();
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::btnAClick(TObject *Sender)
{
	FormMain->SpeedButtonChrBank1->Down=btnA->Down;
    FormMain->SpeedButtonChrBank2->Down=btnB->Down;
}
//---------------------------------------------------------------------------



void __fastcall TFormBankCHR::Image1MouseDown(TObject *Sender,
	  TMouseButton Button, TShiftState Shift, int X, int Y)
{
	int off=0,len=0;

	if(btn256b->Down) {off=Y/8;  len=1;}
	if(btn512b->Down) {off=Y/16; off*=2; len=2;}
	if(btn1k->Down)	  {off=Y/32; off*=4; len=4;}
	if(btn2k->Down)   {off=Y/64; off*=8; len=8;}
	if(btn4k->Down)   {off=0;   len=16;}

	curSelection = TRect(0, off, 16, off+len);
    clickSent=true;
	Draw();
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::Image2MouseDown(TObject *Sender,
      TMouseButton Button, TShiftState Shift, int X, int Y)
{
	int off=0,len=0;
	int tmp_y=Y/2;

	if(btn256b->Down) {off=tmp_y/8;  len=1;}
	if(btn512b->Down) {off=tmp_y/16; off*=2; len=2;}
	if(btn1k->Down)	  {off=tmp_y/32; off*=4; len=4;}
	if(btn2k->Down)   {off=tmp_y/64; off*=8; len=8;}
	if(btn4k->Down)   {off=0;   len=16;}

	bnkSelection = TRect(0, off, 16, off+len);
    clickSent=true;
	Draw();
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::btn4kClick(TObject *Sender)
{
   curSelection = TRect(0, 0, 16, 16);
   bnkSelection = TRect(0, 0, 16, 16);
   Draw();
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::btn2kClick(TObject *Sender)
{
  int len;
  int x,y,w,h;

  if(Sender==btn2k) len=8;
  if(Sender==btn1k) len=4;
  if(Sender==btn512b) len=2;
  if(Sender==btn256b) len=1;

  FormMain->GetSelection(curSelection,x,y,w,h);
  y/=len; y*=len;
  curSelection = TRect(0, y, 16, y+len);

  FormMain->GetSelection(bnkSelection,x,y,w,h);
  y/=len; y*=len;
  bnkSelection = TRect(0, y, 16, y+len);

  Draw();
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::Image1MouseEnter(TObject *Sender)
{
 	curSetHover=true;	
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::Image1MouseLeave(TObject *Sender)
{
	curSetHover=false;
    clickSent=false;
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::Image2MouseLeave(TObject *Sender)
{
	bnkSetHover=false;
	clickSent=false;
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::Image2MouseEnter(TObject *Sender)
{
	bnkSetHover=true;	
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::Image2MouseMove(TObject *Sender,
      TShiftState Shift, int X, int Y)
{
	int off=0,len=0;
	int tmp_y=Y/2;

	if(btn256b->Down) {off=tmp_y/8;  len=1;}
	if(btn512b->Down) {off=tmp_y/16; off*=2; len=2;}
	if(btn1k->Down)	  {off=tmp_y/32; off*=4; len=4;}
	if(btn2k->Down)   {off=tmp_y/64; off*=8; len=8;}
	if(btn4k->Down)   {off=0;   len=16;}

	bnkCursor = TRect(0, off, 16, off+len);
    clickSent=false;
	DrawTimer->Enabled=true;
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::DrawTimerTimer(TObject *Sender)
{
	 if(!openByFileDone) return;
	Draw();
	DrawTimer->Enabled=false;
}
//---------------------------------------------------------------------------

void __fastcall TFormBankCHR::Image1MouseMove(TObject *Sender,
      TShiftState Shift, int X, int Y)
{
	int off=0,len=0;

	if(btn256b->Down) {off=Y/8;  len=1;}
	if(btn512b->Down) {off=Y/16; off*=2; len=2;}
	if(btn1k->Down)	  {off=Y/32; off*=4; len=4;}
	if(btn2k->Down)   {off=Y/64; off*=8; len=8;}
	if(btn4k->Down)   {off=0;   len=16;}

	curCursor = TRect(0, off, 16, off+len);
    clickSent=false;
	DrawTimer->Enabled=true;
}
//---------------------------------------------------------------------------

