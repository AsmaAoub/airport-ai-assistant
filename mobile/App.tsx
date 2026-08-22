import { StatusBar } from 'expo-status-bar';
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
  Pressable,
  Alert,
  ActivityIndicator,
} from 'react-native';

import {
  useAudioRecorder,
  useAudioRecorderState,
  AudioModule,
  setAudioModeAsync,
  createAudioPlayer,
} from 'expo-audio';

import * as FileSystem from 'expo-file-system/legacy';

import { useRef, useState } from 'react';

/*
==========================================================
BACKEND
==========================================================
*/

const API_BASE_URL =
  'https://86b9-41-250-151-107.ngrok-free.app';


export default function App() {

  // ======================================================
  // STATE
  // ======================================================

  const [status, setStatus] =
    useState('Ready');

  const [recordingUri, setRecordingUri] =
    useState<string | null>(null);

  const [transcription, setTranscription] =
    useState('');

  const [assistantResponse, setAssistantResponse] =
    useState('');

  const [isProcessing, setIsProcessing] =
    useState(false);

  const [conversationId, setConversationId] =
    useState<string | null>(null);

  // ======================================================
  // AUDIO PLAYER
  // ======================================================

  const assistantPlayerRef =
    useRef<any>(null);


  // ======================================================
  // AUDIO RECORDER
  // ======================================================

  const audioRecorder =
    useAudioRecorder({});

  const recorderState =
    useAudioRecorderState(
      audioRecorder
    );


  // ======================================================
  // START RECORDING
  // ======================================================

  const startRecording = async () => {

    try {

      console.log(
        '[APP] Requesting microphone permission...'
      );

      setStatus(
        'Requesting microphone...'
      );

      const permission =
        await AudioModule
          .requestRecordingPermissionsAsync();

      if (!permission.granted) {

        console.log(
          '[APP] Microphone permission denied'
        );

        setStatus(
          'Microphone permission denied'
        );

        Alert.alert(
          'Microphone permission',
          'Please allow microphone access to use the voice assistant.'
        );

        return;
      }

      console.log(
        '[APP] Microphone permission granted'
      );


      // --------------------------------------------------
      // AUDIO MODE
      // --------------------------------------------------

      await setAudioModeAsync({

        playsInSilentMode: true,

        allowsRecording: true,

      });

      console.log(
        '[APP] Audio mode configured'
      );


      // --------------------------------------------------
      // PREPARE RECORDER
      // --------------------------------------------------

      await audioRecorder
        .prepareToRecordAsync();

      console.log(
        '[APP] Recorder prepared'
      );


      // --------------------------------------------------
      // START
      // --------------------------------------------------

      audioRecorder.record();

      setStatus(
        'Listening...'
      );

      console.log(
        '[APP] Recording started'
      );

    } catch (error) {

      console.error(
        '[APP] START RECORDING ERROR:',
        error
      );

      setStatus(
        'Error'
      );

      Alert.alert(
        'Recording error',
        'Unable to start the microphone.'
      );
    }
  };


  // ======================================================
  // STOP RECORDING
  // ======================================================

  const stopRecording = async () => {

    try {

      console.log(
        '[APP] Stopping recording...'
      );

      setStatus(
        'Processing...'
      );

      setIsProcessing(
        true
      );


      // --------------------------------------------------
      // STOP
      // --------------------------------------------------

      await audioRecorder.stop();

      console.log(
        '[APP] Recording stopped'
      );


      // --------------------------------------------------
      // URI
      // --------------------------------------------------

      const uri =
        audioRecorder.uri;

      console.log(
        '[APP] Recording URI:',
        uri
      );

      if (!uri) {

        console.error(
          '[APP] No recording URI'
        );

        setStatus(
          'Error'
        );

        setIsProcessing(
          false
        );

        Alert.alert(
          'Recording error',
          'No audio file was created.'
        );

        return;
      }

      setRecordingUri(
        uri
      );


      console.log(
        '========================================'
      );

      console.log(
        '[APP] AUDIO RECORDING CREATED'
      );

      console.log(
        '[APP] URI:',
        uri
      );

      console.log(
        '========================================'
      );


      // --------------------------------------------------
      // SEND
      // --------------------------------------------------

      await sendAudioToBackend(
        uri
      );

    } catch (error) {

      console.error(
        '[APP] STOP RECORDING ERROR:',
        error
      );

      setStatus(
        'Error'
      );

      setIsProcessing(
        false
      );

      Alert.alert(
        'Recording error',
        'Unable to process the recording.'
      );
    }
  };


  // ======================================================
  // PLAY ASSISTANT AUDIO
  // ======================================================

  const playAssistantAudio =
    async (
      uri: string
    ) => {

      try {

        console.log(
          '[APP] Preparing assistant audio...'
        );

        console.log(
          '[APP] Audio URI:',
          uri
        );


        // ------------------------------------------------
        // SWITCH TO PLAYBACK MODE
        // ------------------------------------------------

        await setAudioModeAsync({

          playsInSilentMode: true,

          allowsRecording: false,

        });

        console.log(
          '[APP] Audio mode configured for playback'
        );


        // ------------------------------------------------
        // REMOVE PREVIOUS PLAYER
        // ------------------------------------------------

        if (
          assistantPlayerRef.current
        ) {

          try {

            assistantPlayerRef
              .current
              .pause();

          } catch {}

          try {

            assistantPlayerRef
              .current
              .remove();

          } catch {}

          assistantPlayerRef.current =
            null;
        }


        // ------------------------------------------------
        // CREATE PLAYER
        // ------------------------------------------------

        console.log(
          '[APP] Creating audio player...'
        );

        const player =
          createAudioPlayer(
            uri
          );


        assistantPlayerRef.current =
          player;


        console.log(
          '[APP] Audio player created'
        );


        // ------------------------------------------------
        // PLAY
        // ------------------------------------------------

        player.play();

        console.log(
          '[APP] Assistant audio playback started.'
        );

      } catch (error) {

        console.error(
          '[APP] AUDIO PLAYBACK ERROR:',
          error
        );

        Alert.alert(
          'Audio playback error',
          `Unable to play assistant response.\n\n${String(error)}`
        );
      }
    };


  // ======================================================
  // SEND AUDIO TO BACKEND
  // ======================================================

  const sendAudioToBackend =
    async (
      uri: string
    ) => {

      try {

        console.log(
          '[APP] Sending audio to backend...'
        );

        setStatus(
          'Sending audio...'
        );


        // ------------------------------------------------
        // FORM DATA
        // ------------------------------------------------

        const formData =
          new FormData();


        formData.append(
          'audio',
          {
            uri: uri,

            name:
              'recording.m4a',

            type:
              'audio/m4a',

          } as any
        );


        // ------------------------------------------------
        // CONVERSATION ID
        // ------------------------------------------------

        if (
          conversationId
        ) {

          formData.append(
            'conversation_id',
            conversationId
          );

          console.log(
            '[APP] Conversation ID:',
            conversationId
          );
        }


        // ------------------------------------------------
        // ENDPOINT
        // ------------------------------------------------

        const endpoint =
          `${API_BASE_URL}/api/v1/conversation/audio`;


        console.log(
          '[APP] Backend endpoint:',
          endpoint
        );


        // ------------------------------------------------
        // REQUEST
        // ------------------------------------------------

        const response =
          await fetch(
            endpoint,
            {

              method:
                'POST',

              headers: {

                Accept:
                  'audio/wav, application/json',

              },

              body:
                formData,

            }
          );


        console.log(
          '[APP] HTTP status:',
          response.status
        );


        // ------------------------------------------------
        // CONTENT TYPE
        // ------------------------------------------------

        const contentType =
          response.headers.get(
            'content-type'
          );


        console.log(
          '[APP] Content-Type:',
          contentType
        );


        // =================================================
        // HTTP ERROR
        // =================================================

        if (
          !response.ok
        ) {

          let message =
            `Backend error: ${response.status}`;


          try {

            const errorText =
              await response.text();

            console.error(
              '[APP] Backend error:',
              errorText
            );


            try {

              const errorJson =
                JSON.parse(
                  errorText
                );

              message =
                errorJson?.message ||
                errorJson?.detail ||
                message;

            } catch {

              if (
                errorText
              ) {

                message =
                  errorText;
              }
            }

          } catch {}


          throw new Error(
            message
          );
        }


        // =================================================
        // JSON RESPONSE
        // =================================================

        if (
          contentType &&
          contentType.includes(
            'application/json'
          )
        ) {

          const responseText =
            await response.text();


          console.log(
            '[APP] Raw backend response:',
            responseText
          );


          let data: any;


          try {

            data =
              JSON.parse(
                responseText
              );

          } catch {

            throw new Error(
              `Invalid JSON response from backend: ${responseText}`
            );
          }


          if (
            data.status &&
            data.status !==
              'success'
          ) {

            throw new Error(
              data?.message ||
              'Backend processing failed.'
            );
          }


          throw new Error(
            'Backend returned JSON instead of audio.'
          );
        }


        // =================================================
        // WAV RESPONSE
        // =================================================

        console.log(
          '[APP] Receiving WAV audio...'
        );


        const blob =
          await response.blob();


        console.log(
          '[APP] WAV blob received'
        );


        // -------------------------------------------------
        // ARRAY BUFFER
        // -------------------------------------------------

        /*
         * React Native Blob n'implémente pas toujours
         * blob.arrayBuffer().
         *
         * Response(blob).arrayBuffer()
         * permet de récupérer correctement les bytes.
         */

        const arrayBuffer =
          await new Response(
            blob
          ).arrayBuffer();


        const bytes =
          new Uint8Array(
            arrayBuffer
          );


        console.log(
          '[APP] WAV bytes:',
          bytes.length
        );


        if (
          bytes.length === 0
        ) {

          throw new Error(
            'Backend returned an empty WAV file.'
          );
        }


        // =================================================
        // CONVERT BINARY → BASE64
        // =================================================

        console.log(
          '[APP] Converting WAV to Base64...'
        );


        const chunkSize =
          0x8000;


        let binary =
          '';


        for (
          let i = 0;
          i < bytes.length;
          i += chunkSize
        ) {

          const chunk =
            bytes.subarray(
              i,
              Math.min(
                i + chunkSize,
                bytes.length
              )
            );


          binary +=
            String.fromCharCode(
              ...chunk
            );
        }


        const base64 =
          btoa(
            binary
          );


        console.log(
          '[APP] Base64 generated:',
          base64.length,
          'characters'
        );


        // =================================================
        // SAVE WAV
        // =================================================

        const assistantAudioUri =
          `${FileSystem.cacheDirectory}assistant_response_${Date.now()}.wav`;


        console.log(
          '[APP] Saving assistant WAV...'
        );


        /*
         * IMPORTANT :
         *
         * On utilise directement :
         *
         * encoding: 'base64'
         *
         * et NON :
         *
         * FileSystem.EncodingType.Base64
         *
         * car cette propriété n'existe pas
         * dans ta version actuelle.
         */

        await FileSystem.writeAsStringAsync(
          assistantAudioUri,
          base64,
          {
            encoding:
              'base64',
          } as any
        );


        console.log(
          '[APP] Assistant WAV saved:',
          assistantAudioUri
        );


        // =================================================
        // READ RESPONSE HEADERS
        // =================================================

        const backendConversationId =
          response.headers.get(
            'X-Conversation-Id'
          );


        const backendTranscription =
          response.headers.get(
            'X-Transcription'
          );


        const backendLanguage =
          response.headers.get(
            'X-Language'
          );


        console.log(
          '[APP] Backend conversation ID:',
          backendConversationId
        );


        console.log(
          '[APP] Backend transcription:',
          backendTranscription
        );


        console.log(
          '[APP] Backend language:',
          backendLanguage
        );


        // =================================================
        // UPDATE CONVERSATION
        // =================================================

        if (
          backendConversationId
        ) {

          setConversationId(
            backendConversationId
          );
        }


        // =================================================
        // UPDATE TRANSCRIPTION
        // =================================================

        if (
          backendTranscription
        ) {

          setTranscription(
            backendTranscription
          );
        }


        // =================================================
        // ASSISTANT RESPONSE
        // =================================================

        setAssistantResponse(
          'Assistant response received.'
        );


        // =================================================
        // PLAY
        // =================================================

        setStatus(
          'Playing...'
        );


        await playAssistantAudio(
          assistantAudioUri
        );


        // =================================================
        // FINISHED
        // =================================================

        console.log(
          '========================================'
        );

        console.log(
          '[APP] Conversation processed successfully.'
        );

        console.log(
          '========================================'
        );


        setStatus(
          'Ready'
        );


      } catch (error) {

        console.error(
          '[APP] BACKEND ERROR:',
          error
        );


        setStatus(
          'Backend error'
        );


        Alert.alert(
          'Connection error',
          `Unable to communicate with the backend.\n\n${String(error)}`
        );


      } finally {

        setIsProcessing(
          false
        );
      }
    };


  // ======================================================
  // MICROPHONE BUTTON
  // ======================================================

  const handleMicrophonePress =
    async () => {

      if (
        isProcessing
      ) {

        return;
      }


      try {

        if (
          recorderState.isRecording
        ) {

          await stopRecording();

        } else {

          await startRecording();
        }

      } catch (error) {

        console.error(
          '[APP] MICROPHONE BUTTON ERROR:',
          error
        );
      }
    };


  // ======================================================
  // CURRENT STATE
  // ======================================================

  const isListening =
    recorderState.isRecording;


  // ======================================================
  // UI
  // ======================================================

  return (

    <SafeAreaView
      style={
        styles.container
      }
    >

      <StatusBar
        style="dark"
      />


      <ScrollView
        showsVerticalScrollIndicator={
          false
        }
        contentContainerStyle={
          styles.content
        }
      >


        {/* ================================================
            HEADER
        ================================================= */}

        <View
          style={
            styles.header
          }
        >

          <View>

            <Text
              style={
                styles.brand
              }
            >
              AIRPORT AI
            </Text>


            <Text
              style={
                styles.headerSubtitle
              }
            >
              Conversational AI Assistant
            </Text>

          </View>


          <View
            style={
              styles.statusContainer
            }
          >

            <View
              style={[
                styles.statusDot,

                isListening &&
                  styles.statusDotListening,

                isProcessing &&
                  styles.statusDotProcessing,
              ]}
            />


            <Text
              style={
                styles.statusText
              }
            >
              {status}
            </Text>

          </View>

        </View>


        {/* ================================================
            WELCOME
        ================================================= */}

        <View
          style={
            styles.welcome
          }
        >

          <Text
            style={
              styles.welcomeSmall
            }
          >
            WELCOME
          </Text>


          <Text
            style={
              styles.title
            }
          >

            How can I assist you

            <Text
              style={
                styles.titleBlue
              }
            >
              ?
            </Text>

          </Text>


          <Text
            style={
              styles.description
            }
          >
            Speak naturally with your AI
            assistant. Ask about your flight,
            gate, terminal, or anything
            related to your airport journey.
          </Text>

        </View>


        {/* ================================================
            VOICE
        ================================================= */}

        <View
          style={
            styles.voiceArea
          }
        >

          <View
            style={[
              styles.voiceHalo,

              isListening &&
                styles.voiceHaloActive,

              isProcessing &&
                styles.voiceHaloProcessing,
            ]}
          >

            <View
              style={
                styles.voiceHaloInner
              }
            >

              <Pressable
                onPress={
                  handleMicrophonePress
                }
                disabled={
                  isProcessing
                }
                style={({
                  pressed,
                }) => [

                  styles.microphone,

                  pressed &&
                    styles.microphonePressed,

                  isListening &&
                    styles.microphoneActive,

                  isProcessing &&
                    styles.microphoneProcessing,
                ]}
              >

                {isProcessing ? (

                  <ActivityIndicator
                    size="large"
                    color="#FFFFFF"
                  />

                ) : (

                  <Text
                    style={
                      styles.microphoneIcon
                    }
                  >
                    {isListening
                      ? '■'
                      : '🎙'}
                  </Text>

                )}

              </Pressable>

            </View>

          </View>


          <Text
            style={
              styles.voiceTitle
            }
          >
            {isProcessing
              ? 'Processing...'
              : isListening
              ? 'Listening...'
              : 'Tap to speak'}
          </Text>


          <Text
            style={
              styles.voiceSubtitle
            }
          >
            {isProcessing
              ? 'Your voice is being processed by the AI'
              : isListening
              ? 'Tap again when you are finished'
              : 'Your conversation starts here'}
          </Text>

        </View>


        {/* ================================================
            CONVERSATION
        ================================================= */}

        <View
          style={
            styles.conversationCard
          }
        >

          <View
            style={
              styles.conversationHeader
            }
          >

            <Text
              style={
                styles.conversationTitle
              }
            >
              Conversation
            </Text>


            <View
              style={
                styles.liveContainer
              }
            >

              <View
                style={
                  styles.liveDot
                }
              />

              <Text
                style={
                  styles.liveText
                }
              >
                AI
              </Text>

            </View>

          </View>


          {/* USER */}

          {transcription ? (

            <View
              style={
                styles.message
              }
            >

              <View
                style={
                  styles.userAvatar
                }
              >

                <Text
                  style={
                    styles.avatarText
                  }
                >
                  YOU
                </Text>

              </View>


              <View
                style={
                  styles.messageContent
                }
              >

                <Text
                  style={
                    styles.messageLabel
                  }
                >
                  YOU
                </Text>


                <Text
                  style={
                    styles.messageText
                  }
                >
                  {transcription}
                </Text>

              </View>

            </View>

          ) : null}


          {/* AI */}

          <View
            style={[
              styles.message,

              transcription &&
                styles.aiMessage,
            ]}
          >

            <View
              style={
                styles.avatar
              }
            >

              <Text
                style={
                  styles.avatarText
                }
              >
                AI
              </Text>

            </View>


            <View
              style={
                styles.messageContent
              }
            >

              <Text
                style={
                  styles.messageLabel
                }
              >
                AIRPORT AI
              </Text>


              <Text
                style={
                  styles.messageText
                }
              >
                {assistantResponse ||
                  'Hello. How can I help you today?'}
              </Text>

            </View>

          </View>

        </View>


        {/* ================================================
            AUDIO INFO
        ================================================= */}

        {recordingUri && (

          <View
            style={
              styles.audioInfo
            }
          >

            <Text
              style={
                styles.audioInfoTitle
              }
            >
              Recording captured
            </Text>


            <Text
              style={
                styles.audioInfoText
              }
            >
              Audio sent successfully to
              the AI backend.
            </Text>


            <Text
              style={
                styles.audioUri
              }
              numberOfLines={2}
            >
              {recordingUri}
            </Text>

          </View>

        )}


        {/* ================================================
            TRANSCRIPTION
        ================================================= */}

        {transcription && (

          <View
            style={
              styles.transcriptionCard
            }
          >

            <Text
              style={
                styles.transcriptionTitle
              }
            >
              TRANSCRIPTION
            </Text>


            <Text
              style={
                styles.transcriptionText
              }
            >
              {transcription}
            </Text>

          </View>

        )}


        {/* ================================================
            INFORMATION
        ================================================= */}

        <View
          style={
            styles.suggestion
          }
        >

          <View
            style={
              styles.suggestionIcon
            }
          >

            <Text
              style={
                styles.suggestionIconText
              }
            >
              i
            </Text>

          </View>


          <View
            style={
              styles.suggestionContent
            }
          >

            <Text
              style={
                styles.suggestionLabel
              }
            >
              VOICE ASSISTANT
            </Text>


            <Text
              style={
                styles.suggestionText
              }
            >
              Speak naturally. Your voice
              is sent securely to the AI
              backend where it is transcribed,
              analyzed and processed.
            </Text>

          </View>

        </View>


        {/* ================================================
            FOOTER
        ================================================= */}

        <Text
          style={
            styles.footer
          }
        >
          AI-powered conversational assistant
        </Text>


      </ScrollView>

    </SafeAreaView>
  );
}


// ==========================================================
// STYLES
// ==========================================================

const styles =
  StyleSheet.create({

    container: {
      flex: 1,
      backgroundColor: '#F7FAFC',
    },

    content: {
      paddingHorizontal: 22,
      paddingTop: 20,
      paddingBottom: 35,
    },


    // ====================================================
    // HEADER
    // ====================================================

    header: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: 45,
    },

    brand: {
      fontSize: 17,
      fontWeight: '800',
      letterSpacing: 1.5,
      color: '#123B66',
    },

    headerSubtitle: {
      marginTop: 4,
      fontSize: 11,
      color: '#8A99AA',
    },

    statusContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: 12,
      paddingVertical: 8,
      borderRadius: 20,
      backgroundColor: '#FFFFFF',
      borderWidth: 1,
      borderColor: '#E4EAF0',
    },

    statusDot: {
      width: 7,
      height: 7,
      borderRadius: 4,
      backgroundColor: '#36B37E',
      marginRight: 7,
    },

    statusDotListening: {
      backgroundColor: '#2788C9',
    },

    statusDotProcessing: {
      backgroundColor: '#F59E0B',
    },

    statusText: {
      fontSize: 11,
      fontWeight: '600',
      color: '#52708A',
    },


    // ====================================================
    // WELCOME
    // ====================================================

    welcome: {
      marginBottom: 35,
    },

    welcomeSmall: {
      fontSize: 11,
      fontWeight: '800',
      letterSpacing: 1.4,
      color: '#2D8AC7',
      marginBottom: 9,
    },

    title: {
      fontSize: 31,
      lineHeight: 38,
      fontWeight: '800',
      color: '#18324B',
    },

    titleBlue: {
      color: '#2788C9',
    },

    description: {
      fontSize: 14,
      lineHeight: 21,
      color: '#718096',
      marginTop: 12,
    },


    // ====================================================
    // VOICE
    // ====================================================

    voiceArea: {
      alignItems: 'center',
      marginBottom: 38,
    },

    voiceHalo: {
      width: 190,
      height: 190,
      borderRadius: 95,
      backgroundColor: '#E7F4FC',
      alignItems: 'center',
      justifyContent: 'center',
    },

    voiceHaloActive: {
      backgroundColor: '#D8F0FC',
    },

    voiceHaloProcessing: {
      backgroundColor: '#FFF4DC',
    },

    voiceHaloInner: {
      width: 145,
      height: 145,
      borderRadius: 73,
      backgroundColor: '#D4ECFA',
      alignItems: 'center',
      justifyContent: 'center',
    },

    microphone: {
      width: 100,
      height: 100,
      borderRadius: 50,
      backgroundColor: '#2788C9',
      alignItems: 'center',
      justifyContent: 'center',

      shadowOffset: {
        width: 0,
        height: 7,
      },

      shadowOpacity: 0.2,
      shadowRadius: 12,

      elevation: 8,
    },

    microphoneActive: {
      backgroundColor: '#1F6FA8',
    },

    microphoneProcessing: {
      backgroundColor: '#D99100',
    },

    microphonePressed: {
      transform: [
        {
          scale: 0.94,
        },
      ],
    },

    microphoneIcon: {
      fontSize: 34,
      color: '#FFFFFF',
    },

    voiceTitle: {
      marginTop: 17,
      fontSize: 17,
      fontWeight: '700',
      color: '#18324B',
    },

    voiceSubtitle: {
      marginTop: 5,
      fontSize: 12,
      color: '#8A99AA',
      textAlign: 'center',
    },


    // ====================================================
    // CONVERSATION
    // ====================================================

    conversationCard: {
      backgroundColor: '#FFFFFF',
      borderRadius: 18,
      padding: 17,
      borderWidth: 1,
      borderColor: '#E7EDF2',

      shadowOffset: {
        width: 0,
        height: 3,
      },

      shadowOpacity: 0.05,
      shadowRadius: 8,

      elevation: 2,
    },

    conversationHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: 18,
    },

    conversationTitle: {
      fontSize: 16,
      fontWeight: '700',
      color: '#18324B',
    },

    liveContainer: {
      flexDirection: 'row',
      alignItems: 'center',
    },

    liveDot: {
      width: 6,
      height: 6,
      borderRadius: 3,
      backgroundColor: '#2788C9',
      marginRight: 6,
    },

    liveText: {
      fontSize: 10,
      fontWeight: '700',
      color: '#2788C9',
    },

    message: {
      flexDirection: 'row',
      alignItems: 'flex-start',
    },

    aiMessage: {
      marginTop: 18,
    },

    avatar: {
      width: 38,
      height: 38,
      borderRadius: 19,
      backgroundColor: '#EAF5FC',
      alignItems: 'center',
      justifyContent: 'center',
    },

    userAvatar: {
      width: 38,
      height: 38,
      borderRadius: 19,
      backgroundColor: '#EEF2F6',
      alignItems: 'center',
      justifyContent: 'center',
    },

    avatarText: {
      fontSize: 9,
      fontWeight: '800',
      color: '#2788C9',
    },

    messageContent: {
      flex: 1,
      marginLeft: 11,
    },

    messageLabel: {
      fontSize: 9,
      fontWeight: '800',
      letterSpacing: 1,
      color: '#8A99AA',
    },

    messageText: {
      fontSize: 13,
      lineHeight: 20,
      color: '#45647D',
      marginTop: 4,
    },


    // ====================================================
    // AUDIO
    // ====================================================

    audioInfo: {
      marginTop: 15,
      padding: 15,
      borderRadius: 15,
      backgroundColor: '#F0F8FD',
      borderWidth: 1,
      borderColor: '#DCEFF9',
    },

    audioInfoTitle: {
      fontSize: 13,
      fontWeight: '700',
      color: '#2788C9',
    },

    audioInfoText: {
      fontSize: 11,
      color: '#718096',
      marginTop: 4,
    },

    audioUri: {
      fontSize: 9,
      color: '#9AA8B5',
      marginTop: 8,
    },


    // ====================================================
    // TRANSCRIPTION
    // ====================================================

    transcriptionCard: {
      marginTop: 15,
      padding: 15,
      borderRadius: 15,
      backgroundColor: '#FFFFFF',
      borderWidth: 1,
      borderColor: '#E7EDF2',
    },

    transcriptionTitle: {
      fontSize: 9,
      fontWeight: '800',
      letterSpacing: 1.2,
      color: '#8A99AA',
    },

    transcriptionText: {
      marginTop: 6,
      fontSize: 13,
      lineHeight: 20,
      color: '#45647D',
    },


    // ====================================================
    // INFO
    // ====================================================

    suggestion: {
      marginTop: 18,
      padding: 15,
      borderRadius: 17,
      backgroundColor: '#EAF6FC',
      flexDirection: 'row',
      alignItems: 'center',
    },

    suggestionIcon: {
      width: 38,
      height: 38,
      borderRadius: 12,
      backgroundColor: '#FFFFFF',
      alignItems: 'center',
      justifyContent: 'center',
    },

    suggestionIconText: {
      fontSize: 16,
      fontWeight: '700',
      color: '#2788C9',
    },

    suggestionContent: {
      flex: 1,
      marginLeft: 12,
    },

    suggestionLabel: {
      fontSize: 9,
      fontWeight: '800',
      letterSpacing: 1.2,
      color: '#2788C9',
    },

    suggestionText: {
      fontSize: 12,
      lineHeight: 18,
      color: '#45647D',
      marginTop: 4,
    },


    // ====================================================
    // FOOTER
    // ====================================================

    footer: {
      textAlign: 'center',
      alignSelf: 'center',
      marginTop: 28,
      fontSize: 10,
      color: '#AAB6C2',
    },

  });